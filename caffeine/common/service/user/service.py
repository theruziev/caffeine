from typing import Tuple, List

from aio_pubsub.interfaces import PubSub
from pendulum import now

from caffeine.common.service.user.schema import (
    LoginSchema,
    RegisterUserSchema,
    ResetPasswordRequestSchema,
)
from caffeine.common.security import generate_random
from caffeine.common.security.password import bcrypt_hash, bcrypt_verify
from caffeine.common.schema.mail import EmailMessage
from caffeine.common.service.user.errors import UserExistError, UserNotExistError
from caffeine.common.settings import Settings
from caffeine.common.store import Paginator
from caffeine.common.store.postgresql.db import DoesNotExistException
from caffeine.common.store.user import (
    User,
    UserStatusEnum,
    UserStore,
    UserSort,
    UserFilter,
    UserTypeEnum,
)
from caffeine.common.template import Templater


class UserService:
    def __init__(
        self, settings: Settings, user_store: UserStore, pubsub: PubSub, templater: Templater
    ):
        self.settings = settings
        self.user_store = user_store
        self.pubsub = pubsub
        self.templater = templater

    async def register(self, schema: RegisterUserSchema) -> User:
        user = User(
            email=schema.email,
            password=bcrypt_hash(schema.password),
            created_at=now().int_timestamp,
            updated_at=now().int_timestamp,
            activation_code=generate_random(16),
        )
        exist = await self.user_store.exist_by_email(schema.email)
        if exist:
            raise UserExistError(f"User with email: {schema.email} exists")

        user = await self.user_store.add(user)
        await self._send_register_email(user)
        return user

    async def activate(self, token: str) -> User:
        try:
            user = await self.user_store.find_by_activation_code(token)
            user.status = UserStatusEnum.active
            user.activation_code = None
            user.touch()
            return await self.user_store.update(user)
        except DoesNotExistException:
            raise UserNotExistError(f"User with token: {token} does not exist")

    async def reset_password_request(self, schema: ResetPasswordRequestSchema) -> User:
        try:
            user = await self.user_store.find_by_email(schema.email)
            user.reset_password_code = generate_random(16)
            user.touch()
            user = await self.user_store.update(user)
            await self._send_reset_password_email(user)
            return user
        except DoesNotExistException:
            raise UserNotExistError(f"User with token: {schema.email} does not exist")

    async def get_by_reset_password_code(self, token: str) -> User:
        try:
            return await self.user_store.find_by_reset_password_code(token)
        except DoesNotExistException:
            raise UserNotExistError(f"User with token: {token} does not exist.")

    async def reset_password(self, user: User, password: str):
        user.password = bcrypt_hash(password)
        user.touch()
        return await self.user_store.update(user)

    async def auth(self, schema: LoginSchema) -> User:
        try:
            user = await self.user_store.find_by_email(schema.email)
            if bcrypt_verify(schema.password, user.password):
                return user
        except DoesNotExistException:
            pass

        raise UserNotExistError(f"User with email: {schema.email} does not exist.")

    async def get_by_id(self, uid: str):
        try:
            return await self.user_store.find_by_id(uid)
        except DoesNotExistException:
            raise UserNotExistError(f"User: '{uid}' does'nt exist")

    async def change_status(self, user: User, status: UserStatusEnum):
        user.status = status
        user.touch()
        return await self.user_store.update(user)

    async def change_type(self, user: User, user_type: UserTypeEnum):
        user.type = user_type
        user.touch()
        return await self.user_store.update(user)

    async def search(
        self, user_filter: UserFilter = None, sort: UserSort = None, paginator: Paginator = None
    ) -> Tuple[List[User], int]:
        return await self.user_store.search(user_filter, sort, paginator)

    async def _send_register_email(self, user: User):
        activation_link = "{}{}".format(
            self.settings.ACTIVATION_LINK_TEMPLATE, user.activation_code
        )
        body = await self.templater.load(
            "/email/register.html", {"activation_link": activation_link}
        )
        msg = EmailMessage(to=user.email, subject="Registration User", html=body)
        await self.pubsub.publish("reg_email", msg.dict())

    async def _send_reset_password_email(self, user: User):
        reset_password_link = "{}{}".format(
            self.settings.RESET_PASSWORD_LINK_TEMPLATE, user.reset_password_code
        )
        body = await self.templater.load(
            "email/reset_password.html", {"reset_password_link": reset_password_link}
        )
        msg = EmailMessage(to=user.email, subject="Reset User", html=body)
        await self.pubsub.publish("reset_email", msg.dict())
