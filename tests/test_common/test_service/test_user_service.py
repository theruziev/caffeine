import pytest
from asynctest import patch, Mock, MagicMock
from faker import Faker

from caffeine.common.pubsub import PostgresPubSub
from caffeine.common.service.user.schema import (
    RegisterUserSchema,
    ActivationSchema,
    ResetPasswordRequestSchema,
    LoginSchema,
)
from caffeine.common.security.password import bcrypt_hash, bcrypt_verify
from caffeine.common.service.user.errors import UserExistError, UserNotExistError
from caffeine.common.service.user.service import UserService
from caffeine.common.settings import Settings
from caffeine.common.store.postgresql.db import DoesNotExistException, PostgreSQLDb
from caffeine.common.store.postgresql.user import PostgreSQLUserStore
from caffeine.common.store.user import UserStatusEnum, UserTypeEnum
from caffeine.common.template import Templater
from caffeine.common.test_utils.user_store import gen_user

fake = Faker()


@pytest.fixture(scope="function")
def user_store():
    return PostgreSQLUserStore(MagicMock(PostgreSQLDb("")))


@pytest.fixture(scope="function")
def user_service(user_store):
    user_service = UserService(Settings(), user_store, Mock(PostgresPubSub), Mock(Templater("")))
    user_service.templater.load.return_value = "blah"
    return user_service


def gen_reg_form():
    data = {"email": fake.free_email(), "password": fake.password()}

    return RegisterUserSchema(**data)


@pytest.mark.asyncio
async def test_register(user_service):
    with patch.object(PostgreSQLUserStore, "exist_by_email", return_value=True):
        with pytest.raises(UserExistError):
            await user_service.register(gen_reg_form())

    with patch.object(PostgreSQLUserStore, "exist_by_email", return_value=False):
        with patch.object(PostgreSQLUserStore, "add") as add:
            form = gen_reg_form()

            def side_effect_check(user):
                assert user.email == form.email
                return user

            add.side_effect = side_effect_check
            await user_service.register(form)


@pytest.mark.asyncio
async def test_activate(user_service):
    with patch.object(
        PostgreSQLUserStore, "find_by_activation_code", side_effect=DoesNotExistException
    ):
        with pytest.raises(UserNotExistError):
            schema = ActivationSchema(token="token")
            await user_service.activate(schema)

    with patch.object(PostgreSQLUserStore, "find_by_activation_code") as p:
        user = gen_user()
        user.activation_code = "token"
        p.return_value = user
        with patch.object(PostgreSQLUserStore, "update") as add:

            def side_effect_check(u):
                assert u.activation_code is None

            add.side_effect = side_effect_check
            await user_service.activate("token")


@pytest.mark.asyncio
async def test_reset_password_request(user_service):
    with patch.object(PostgreSQLUserStore, "find_by_email", side_effect=DoesNotExistException):
        with pytest.raises(UserNotExistError):
            schema = ResetPasswordRequestSchema(email="email@email.com")
            await user_service.reset_password_request(schema)

    with patch.object(PostgreSQLUserStore, "find_by_email") as p:
        schema = ResetPasswordRequestSchema(email="email@email.com")
        user = gen_user()
        user.email = schema.email

        p.return_value = user
        with patch.object(PostgreSQLUserStore, "update") as add:

            def side_effect_check(u):
                assert u.reset_password_code
                assert u.email == user.email
                return user

            add.side_effect = side_effect_check
            await user_service.reset_password_request(schema)


@pytest.mark.asyncio
async def test_get_by_reset_password_code(user_service):
    with patch.object(
        PostgreSQLUserStore, "find_by_reset_password_code", side_effect=DoesNotExistException
    ):
        with pytest.raises(UserNotExistError):
            await user_service.get_by_reset_password_code("token")

    with patch.object(PostgreSQLUserStore, "find_by_reset_password_code") as p:
        user = gen_user()

        p.return_value = user

        u = await user_service.get_by_reset_password_code("token")
        assert u == user


@pytest.mark.asyncio
async def test_reset_password(user_store, user_service):
    user = gen_user()
    user_store = Mock(user_store)

    def side_effect_check(u):
        assert bcrypt_verify("password", u.password)

    user_store.update.side_effect = side_effect_check
    user_service.user_store = user_store
    await user_service.reset_password(user, "password")


@pytest.mark.asyncio
async def test_auth(user_store, user_service):
    user_service.user_store = user_store

    user = gen_user()
    user.password = bcrypt_hash("hello_password")
    schema = LoginSchema(email=user.email, password="hello_password")
    with patch.object(PostgreSQLUserStore, "find_by_email", return_value=user):
        u = await user_service.auth(schema)
        assert user == u

        wrong_pass_schema = LoginSchema(email=user.email, password="wrong_password")
        with pytest.raises(UserNotExistError):
            await user_service.auth(wrong_pass_schema)

    with patch.object(PostgreSQLUserStore, "find_by_email", side_effect=DoesNotExistException):
        with pytest.raises(UserNotExistError):
            await user_service.auth(schema)


@pytest.mark.asyncio
async def test_get_by_id(user_store, user_service):
    user = gen_user()

    user_store = Mock(user_store)
    user_store.find_by_id.side_effect = [user, DoesNotExistException]
    user_service.user_store = user_store
    u = await user_service.get_by_id(user.id)
    assert user == u

    with pytest.raises(UserNotExistError):
        await user_service.get_by_id(user.id)


@pytest.mark.asyncio
async def test_change_status(user_store, user_service):
    user = gen_user()
    user.updated_at = 0

    user_store = Mock(user_store)

    def side_effect_check(u):
        assert u.status == status
        assert u.updated_at != 0

    user_store.update.side_effect = side_effect_check
    user_service.user_store = user_store
    status = UserStatusEnum.inactive

    await user_service.change_status(user, status)


@pytest.mark.asyncio
async def test_change_type(user_store, user_service):

    user_store = Mock(user_store)
    user = gen_user()
    user.updated_at = 0

    def side_effect_check(u):
        assert u.type == user_type
        assert u.updated_at != 0

    user_store.update.side_effect = side_effect_check
    user_service.user_store = user_store

    user_type = UserTypeEnum.gdpr_removed
    await user_service.change_type(user, user_type)


@pytest.mark.asyncio
async def test_search_user(user_store, user_service):

    user_store = Mock(user_store)
    true_users, true_cnt = [gen_user() for i in range(5)], len(range(5))
    user_store.search.return_value = true_users, true_cnt
    user_service.user_store = user_store
    user_service = UserService(Settings(), user_store, Mock(PostgresPubSub), Mock(Templater))
    users, cnt = await user_service.search()
    assert true_users == users
    assert true_cnt == cnt
