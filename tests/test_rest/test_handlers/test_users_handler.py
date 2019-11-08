import pytest
from asynctest import Mock
from faker import Faker
from pendulum import now
from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.routing import Router
from starlette.testclient import TestClient
from urouter.exporters.starlette_exporter import StarletteRouter

from caffeine.common.pubsub import PostgresPubSub
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
from caffeine.rest.utils.captcha import Recaptcha

fake = Faker()

jwt_helper = JwtHelper("JWTSECRET")
security_container = SecurityContainer(jwt_helper, Enforcer(Mock()))


@pytest.fixture
def app():
    def wrapper(user_service, recaptcha=True):
        app = Starlette()
        r = Mock(Recaptcha(""))
        r.check.return_value = recaptcha
        ExceptionHandlers(app)
        settings = Settings()
        settings.JWT_TOKEN_EXPIRE = 10
        settings.JWT_TOKEN_REFRESH_EXPIRE = 50
        user_handler = UserHandler(settings, user_service, security_container, r)
        router = StarletteRouter(app)

        def user_routes():
            user_private_router = router.make_router()
            u = user_private_router.make_router()
            u.get("/{uid:str}/", need_auth(user_handler.get_by_id, ["admin"]))
            u.get("/{uid:str}/change_status", need_auth(user_handler.change_status, ["admin"]))
            u.get("/{uid:str}/change_type", need_auth(user_handler.change_type, ["admin"]))
            user_private_router.mount("/u", u)
            user_private_router.get("/me", need_auth(user_handler.get_by_id))

            user_public_router = router.make_router()
            user_public_router.post("/register", user_handler.register)
            user_public_router.get("/activate/{token:str}", user_handler.activate)
            user_public_router.post("/reset-password", user_handler.reset_password_request)
            user_public_router.get("/reset-password/{token:str}", user_handler.reset_password_check)
            user_public_router.post("/reset-password/{token:str}", user_handler.reset_password)
            user_public_router.post("/search", user_handler.search)
            user_public_router.post("/auth", user_handler.auth)
            user_public_router.post("/refresh", user_handler.refresh)

            user_router = router.make_router()
            user_router.mount("/user", user_public_router)
            user_router.mount("/user", user_private_router)
            return user_router

        app.add_middleware(
            AuthenticationMiddleware,
            backend=JwtAuthBackend(user_service, security_container.jwt_helper),
        )
        router.mount("/v1", user_routes)
        router.export()

        return app

    return wrapper


@pytest.fixture
def user_service():
    templater = Mock(Templater(""))
    templater.load.return_value = "blah"
    return Mock(UserService(Settings(), Mock(), Mock(), templater))


@pytest.mark.parametrize(
    "status_code, key, side_effect",
    [(200, "success", lambda x: gen_user()), (409, "error", UserExistError)],
)
def test_register(app, user_service, status_code, key, side_effect):
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
def test_register_validation(app, user_service, email, password, fields):
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
def test_activate(app, user_service, side_effect, code):
    user_service.activate.side_effect = side_effect
    client = TestClient(app(user_service))
    token = fake.pystr(min_chars=20, max_chars=40)
    response = client.get(f"v1/user/activate/{token}")
    assert response.status_code == code


@pytest.mark.parametrize(
    "side_effect,code", [(UserNotExistError, 404), (lambda x: gen_user(), 200)]
)
def test_reset_password_request(app, user_service, side_effect, code):
    user_service.reset_password_request.side_effect = side_effect
    client = TestClient(app(user_service))
    data = {"email": "email@example.com", "captcha": "blah"}
    response = client.post(f"v1/user/reset-password", json=data)
    assert response.status_code == code


@pytest.mark.parametrize(
    "side_effect,code", [(UserNotExistError, 404), (lambda x: gen_user(), 200)]
)
def test_reset_password_check(app, user_service, side_effect, code):
    user_service.get_by_reset_password_code.side_effect = side_effect
    client = TestClient(app(user_service))
    token = fake.pystr(min_chars=20, max_chars=40)
    response = client.get(f"v1/user//reset-password/{token}")
    assert response.status_code == code


@pytest.mark.parametrize(
    "side_effect,code", [(UserNotExistError, 404), (lambda x, y: gen_user(), 200)]
)
def test_reset_password(app, user_service, side_effect, code):
    user_service.reset_password.side_effect = side_effect
    user_service.reset_password.side_effect = side_effect
    client = TestClient(app(user_service))
    token = fake.pystr(min_chars=20, max_chars=40)
    data = {"password": "new-password"}
    response = client.post(f"v1/user/reset-password/{token}", json=data)
    assert response.status_code == code


@pytest.mark.parametrize(
    "side_effect,code", [(UserNotExistError, 401), (lambda x: gen_user(), 200)]
)
def test_auth(app, user_service, side_effect, code):
    user_service.auth.side_effect = side_effect
    client = TestClient(app(user_service))
    data = {"email": "email@example.com", "password": "password", "captcha": "blah"}
    response = client.post("v1/user/auth", json=data)
    assert response.status_code == code
    user = gen_user()
    payload = {"sub": user.id}
    token = jwt_helper.encode(payload)
    header = {"Authorization": f"Bearer {token}"}


def test_get_by_id(app, user_service):
    user = gen_user(True)
    user_service.get_by_id.side_effect = lambda x: user
    client = TestClient(app(user_service))
    payload = {"sub": user.id, "scp": [UserRoleEnum.admin]}
    token = jwt_helper.encode(payload)
    header = {"Authorization": f"Bearer {token}"}

    response = client.get(f"v1/user/u/{user.id}", headers=header)
    assert response.status_code == 200
    data = response.json()
    assert user.id == data["id"]
    assert user.status == data["status"]
    assert user.type == data["type"]


def test_get_by_id_failed(app, user_service):
    user = gen_user()
    user_service.get_by_id.side_effect = [user, user, UserNotExistError]
    client = TestClient(app(user_service))
    payload = {"sub": user.id, "scp": [UserRoleEnum.admin]}
    token = jwt_helper.encode(payload)
    header = {"Authorization": f"Bearer {token}"}

    response = client.get(f"v1/user/u/wrong_id", headers=header)
    assert response.status_code == 404


def test_user_me(app, user_service):
    user = gen_user(True)
    user_service.get_by_id.side_effect = [user, user, user]
    client = TestClient(app(user_service))
    payload = {"sub": user.id}
    token = jwt_helper.encode(payload)
    header = {"Authorization": f"Bearer {token}"}

    response = client.get(f"v1/user/me", headers=header)
    assert response.status_code == 200
    data = response.json()
    assert user.id == data["id"]
    assert user.status == data["status"]
    assert user.type == data["type"]


def test_user_me_wrong_jwt(app, user_service):
    user = gen_user()
    user_service.get_by_id.side_effect = [user, user, user]
    client = TestClient(app(user_service))

    # Wrong jwt
    payload = {"sub": user.id}
    jwt_helper2 = JwtHelper("OTHER_SECRET")
    token = jwt_helper2.encode(payload)
    header = {"Authorization": f"Bearer {token}"}
    response = client.get(f"v1/user/me", headers=header)
    assert response.status_code == 400

    # Expired jwt
    payload = {"sub": user.id, "exp": now().int_timestamp - 10}
    token = jwt_helper2.encode(payload)
    header = {"Authorization": f"Bearer {token}"}
    response = client.get(f"v1/user/me", headers=header)
    assert response.status_code == 400

    # Wrong header
    payload = {"sub": user.id}
    token = jwt_helper.encode(payload)
    header = {"Authorization": f"sdf {token}"}
    response = client.get(f"v1/user/me", headers=header)
    assert response.status_code == 403

    # Refresh token in auth
    payload = {"sub": user.id, "scp": ["refresh"]}
    token = jwt_helper.encode(payload)
    header = {"Authorization": f"Bearer {token}"}
    response = client.get(f"v1/user/me", headers=header)
    assert response.status_code == 403


@pytest.mark.parametrize("scope, status_code", [(SystemScopes.refresh, 200), ("error_scope", 403)])
def test_refresh(app, user_service, scope, status_code):
    user = gen_user()
    user_service.get_by_id.return_value = user
    client = TestClient(app(user_service))
    payload = {"sub": user.id, "scp": [scope]}

    token = jwt_helper.encode(payload)
    response = client.post("/v1/user/refresh", json={"token": token})
    assert response.status_code == status_code


def test_refresh_wrong_token(app, user_service):
    user = gen_user()
    user_service.get_by_id.return_value = user
    client = TestClient(app(user_service))
    payload = {"sub": user.id, "scp": [SystemScopes.refresh], "exp": 0}

    token = jwt_helper.encode(payload)
    response = client.post("/v1/user/refresh", json={"token": token})
    assert response.status_code == 403

    payload = {"sub": user.id, "scp": [SystemScopes.refresh]}
    jwt_helper2 = JwtHelper("OTHER_SECRET")
    token = jwt_helper2.encode(payload)
    response = client.post("/v1/user/refresh", json={"token": token})
    assert response.status_code == 403


def test_search(app, user_service):
    true_users, true_cnt = [gen_user(True) for i in range(5)], len(range(5))
    user_service.search.return_value = true_users, true_cnt
    user = gen_user()
    client = TestClient(app(user_service))
    payload = {"sub": user.id, "scp": [UserRoleEnum.admin]}
    header = {"Authorization": f"Bearer {jwt_helper.encode(payload)}"}
    response = client.post(f"v1/user/search", json={}, headers=header)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == true_cnt
    ids = [u["id"] for u in data["rows"]]
    assert ids == [u.id for u in true_users]
