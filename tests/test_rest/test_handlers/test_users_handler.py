import pytest
from asynctest import Mock
from faker import Faker
from pendulum import now
from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.testclient import TestClient
from urouter.exporters.starlette_exporter import StarletteRouter

from caffeine.common.security.casbin import Enforcer
from caffeine.common.security.jwt import JwtHelper
from caffeine.common.service.user.errors import UserExistError, UserNotExistError
from caffeine.common.service.user.service import UserService
from caffeine.common.settings import Settings
from caffeine.common.store.user import UserRoleEnum
from caffeine.common.template import Templater
from caffeine.common.test_utils.user_store import gen_user
from caffeine.rest.auth import JwtAuthBackend, SystemScopes, need_auth
from caffeine.rest.handlers.exception_handlers import ExceptionHandlers
from caffeine.rest.handlers.users.handlers import UserHandler
from caffeine.rest.containers import SecurityContainer
from caffeine.rest.handlers.users.routers import UserRouter
from caffeine.rest.utils.captcha import Recaptcha

fake = Faker()

jwt_helper = JwtHelper("JWTSECRET")
security_container = SecurityContainer(
    jwt_helper, Enforcer(Mock()), "AuthorizationToken", "RefreshToken", 2500
)


def app(user_service, recaptcha=True):
    starlette = Starlette()
    r = Mock(Recaptcha(""))
    r.check.return_value = recaptcha
    ExceptionHandlers(starlette)
    settings = Settings()
    settings.JWT_TOKEN_EXPIRE = 10
    settings.JWT_TOKEN_REFRESH_EXPIRE = 50
    user_handler = UserHandler(settings, user_service, security_container, r)
    router = StarletteRouter(starlette)
    auth_middleware = AuthenticationMiddleware(
        starlette,
        backend=JwtAuthBackend(
            user_service, security_container.jwt_helper, security_container.jwt_cookie_key
        ),
    )
    user_routers = UserRouter(user_handler, auth_middleware, router)
    router.mount("/v1", user_routers.init())
    router.export()

    return starlette


@pytest.fixture
def user_service():
    templater = Mock(Templater(""))
    templater.load.return_value = "blah"
    return Mock(UserService(Settings(), Mock(), Mock(), templater))


@pytest.mark.parametrize(
    "status_code, key, side_effect",
    [(200, "success", lambda x: gen_user()), (409, "error", UserExistError)],
)
def test_register(user_service, status_code, key, side_effect):
    user_service.register.side_effect = side_effect
    client = TestClient(app(user_service))

    data = {"email": "test@example.com", "password": "password", "captcha": "blah"}

    response = client.post("v1/user/register", json=data)
    assert response.status_code == status_code
    res = response.json()
    assert res.get(key)


@pytest.mark.parametrize(
    "email,password,fields",
    [
        ("test", "password", ["email"]),
        ("test@example.com", "", ["password"]),
        ("", "", ["email", "password"]),
        ("test@example.com", "min", ["password"]),
    ],
)
def test_register_validation(user_service, email, password, fields):
    client = TestClient(app(user_service))

    data = {"email": email, "password": password, "captcha": "blah"}

    response = client.post("v1/user/register", json=data)
    assert response.status_code == 400
    res = response.json()
    errors_fields = [l for r in res for l in r["loc"]]
    for f in errors_fields:
        assert f in fields


@pytest.mark.parametrize(
    "side_effect,code", [(UserNotExistError, 404), (lambda x: gen_user(), 200)]
)
def test_activate(user_service, side_effect, code):
    user_service.activate.side_effect = side_effect
    client = TestClient(app(user_service))
    token = fake.pystr(min_chars=20, max_chars=40)
    response = client.get(f"v1/user/activate/{token}")
    assert response.status_code == code


@pytest.mark.parametrize(
    "side_effect,code", [(UserNotExistError, 404), (lambda x: gen_user(), 200)]
)
def test_reset_password_request(user_service, side_effect, code):
    user_service.reset_password_request.side_effect = side_effect
    client = TestClient(app(user_service))
    data = {"email": "email@example.com", "captcha": "blah"}
    response = client.post(f"v1/user/reset-password", json=data)
    assert response.status_code == code


@pytest.mark.parametrize(
    "side_effect,code", [(UserNotExistError, 404), (lambda x: gen_user(), 200)]
)
def test_reset_password_check(user_service, side_effect, code):
    user_service.get_by_reset_password_code.side_effect = side_effect
    client = TestClient(app(user_service))
    token = fake.pystr(min_chars=20, max_chars=40)
    response = client.get(f"v1/user/reset-password/{token}")
    assert response.status_code == code


@pytest.mark.parametrize(
    "side_effect,code", [(UserNotExistError, 404), (lambda x, y: gen_user(), 200)]
)
def test_reset_password(user_service, side_effect, code):
    user_service.reset_password.side_effect = side_effect
    user_service.reset_password.side_effect = side_effect
    client = TestClient(app(user_service))
    token = fake.pystr(min_chars=20, max_chars=40)
    data = {"password": "new-password"}
    response = client.post(f"v1/user/reset-password/{token}", json=data)
    assert response.status_code == code


@pytest.mark.parametrize(
    "side_effect,code", [(UserNotExistError, 401), (lambda x: gen_user(True), 200)]
)
def test_auth(user_service, side_effect, code):
    user_service.auth.side_effect = side_effect
    client = TestClient(app(user_service))
    data = {"email": "email@example.com", "password": "password", "captcha": "blah"}
    response = client.post("v1/user/auth", json=data)
    assert response.status_code == code, response.text


def test_get_by_id(user_service):
    user = gen_user(True)
    user_service.get_by_id.side_effect = [user, user]
    client = TestClient(app(user_service))
    payload = {"sub": user.id, "scp": [UserRoleEnum.admin]}
    token = jwt_helper.encode(payload)
    cookies = {security_container.jwt_cookie_key: token}

    response = client.get(f"v1/user/u/{user.id}", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert user.id == data["id"]
    assert user.status == data["status"]
    assert user.type == data["type"]


def test_get_by_id_failed(user_service):
    user = gen_user(True)
    user_service.get_by_id.side_effect = [user, UserNotExistError]
    client = TestClient(app(user_service))
    payload = {"sub": user.id, "scp": [UserRoleEnum.admin]}
    token = jwt_helper.encode(payload)
    cookies = {security_container.jwt_cookie_key: token}

    response = client.get(f"v1/user/u/wrong_id", cookies=cookies)
    assert response.status_code == 404, response.text


def test_user_me(user_service):
    user = gen_user(True)
    user_service.get_by_id.side_effect = [user, user, user, user, user]
    client = TestClient(app(user_service))
    payload = {"sub": user.id}
    token = jwt_helper.encode(payload)
    cookies = {security_container.jwt_cookie_key: token}

    response = client.get(f"v1/user/me", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert user.id == data["id"]
    assert user.status == data["status"]
    assert user.type == data["type"]


def test_user_me_wrong_jwt(user_service):
    user = gen_user()
    user_service.get_by_id.side_effect = [user, user, user]
    client = TestClient(app(user_service))

    # Wrong jwt
    payload = {"sub": user.id}
    jwt_helper2 = JwtHelper("OTHER_SECRET")
    token = jwt_helper2.encode(payload)
    cookies = {security_container.jwt_cookie_key: token}
    response = client.get(f"v1/user/me", cookies=cookies)
    assert response.status_code == 400

    # Expired jwt
    payload = {"sub": user.id, "exp": now().int_timestamp - 10}
    token = jwt_helper2.encode(payload)
    cookies = {security_container.jwt_cookie_key: token}
    response = client.get(f"v1/user/me", cookies=cookies)
    assert response.status_code == 400

    cookies = {security_container.jwt_cookie_key: f"blah blah"}
    response = client.get(f"v1/user/me", cookies=cookies)
    assert response.status_code == 400

    # Refresh token in auth
    payload = {"sub": user.id, "scp": ["refresh"]}
    token = jwt_helper.encode(payload)
    cookies = {security_container.jwt_cookie_key: token}
    response = client.get(f"v1/user/me", cookies=cookies)
    assert response.status_code == 403


@pytest.mark.parametrize("scope, status_code", [(SystemScopes.refresh, 200), ("error_scope", 403)])
def test_refresh(user_service, scope, status_code):
    user = gen_user()
    user_service.get_by_id.return_value = user
    client = TestClient(app(user_service))
    payload = {"sub": user.id, "scp": [scope]}

    token = jwt_helper.encode(payload)
    response = client.post(
        "/v1/user/refresh", cookies={security_container.jwt_cookie_refresh_key: token}
    )
    assert response.status_code == status_code


def test_refresh_wrong_token(user_service):
    user = gen_user()
    user_service.get_by_id.return_value = user
    client = TestClient(app(user_service))
    payload = {"sub": user.id, "scp": [SystemScopes.refresh], "exp": 0}

    token = jwt_helper.encode(payload)
    response = client.post(
        "/v1/user/refresh", cookies={security_container.jwt_cookie_refresh_key: token}
    )
    assert response.status_code == 403

    payload = {"sub": user.id, "scp": [SystemScopes.refresh]}
    jwt_helper2 = JwtHelper("OTHER_SECRET")
    token = jwt_helper2.encode(payload)
    response = client.post(
        "/v1/user/refresh", cookies={security_container.jwt_cookie_refresh_key: token}
    )
    assert response.status_code == 403


def test_search(user_service):
    true_users, true_cnt = [gen_user(True) for i in range(5)], len(range(5))
    user_service.search.return_value = true_users, true_cnt
    user = gen_user()
    client = TestClient(app(user_service))
    payload = {"sub": user.id, "scp": [UserRoleEnum.admin]}
    cookies = {security_container.jwt_cookie_key: jwt_helper.encode(payload)}
    response = client.post(f"v1/user/search", json={}, cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == true_cnt
    ids = [u["id"] for u in data["rows"]]
    assert ids == [u.id for u in true_users]
