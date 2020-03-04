import typing
from time import time

from pendulum import now
from starlette.requests import Request

from caffeine.common.service.user.errors import UserExistError, UserNotExistError
from caffeine.common.service.user.schema import (
    RegisterUserSchema,
    ResetPasswordRequestSchema,
    LoginSchema,
)
from caffeine.common.service.user.service import UserService
from caffeine.common.settings import Settings
from caffeine.common.store import Paginator
from caffeine.common.store.user import UserFilter, UserSort, User
from caffeine.rest.auth import SystemScopes
from caffeine.rest.containers import SecurityContainer
from caffeine.rest.handlers import Handler
from caffeine.rest.handlers.exception_handlers import NotFoundError
from caffeine.rest.handlers.users.schemas import (
    UserSearchResponse,
    UserSearchRequest,
    RegisterRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    UserResponse,
    ChangeStatusRequest,
    ChangeTypeRequest,
    UserLoginRequest,
    Token,
)
from caffeine.rest.logger import logger
from caffeine.rest.utils.captcha import Recaptcha


class UserHandler(Handler):
    def __init__(
        self,
        settings: Settings,
        user_service: UserService,
        security: SecurityContainer,
        recaptcha: Recaptcha,
    ):
        self.user_service = user_service
        self.jwt_helper = security.jwt_helper
        self.security = security
        self.token_expire = settings.JWT_TOKEN_EXPIRE
        self.refresh_token_expire = settings.JWT_TOKEN_REFRESH_EXPIRE
        self.recaptcha = recaptcha

    async def register(self, request: Request):
        data = await request.json()
        register_form = RegisterRequest(**data)
        if not await self.recaptcha.check(register_form.captcha):
            return self.error_message("Captcha error", status_code=400)
        try:
            schema = RegisterUserSchema(**register_form.dict())
            user = await self.user_service.register(schema)
            return self.json(UserResponse(**user.dict()))
        except UserExistError:
            return self.error_message(f"User {register_form.email} already exists", status_code=409)

    async def activate(self, request: Request):
        try:
            token = request.path_params.get("token")
            await self.user_service.activate(token)
            return self.success()
        except UserNotExistError:
            return self.not_found()

    async def reset_password_request(self, request: Request):
        data = await request.json()
        reset_password = ResetPasswordRequest(**data)
        if not await self.recaptcha.check(reset_password.captcha):
            return self.error_message("Captcha error", status_code=400)
        try:
            schema = ResetPasswordRequestSchema(**reset_password.dict())
            await self.user_service.reset_password_request(schema)
            return self.success()
        except UserNotExistError:
            return self.not_found()

    async def reset_password_check(self, request: Request):
        token = request.path_params.get("token")
        try:
            await self.user_service.get_by_reset_password_code(token)
            return self.success()
        except UserNotExistError:
            return self.not_found()

    async def reset_password(self, request: Request):
        token = request.path_params.get("token")
        data = await request.json()
        change_password = ChangePasswordRequest(**data)
        try:
            user = await self.user_service.get_by_reset_password_code(token)
            await self.user_service.reset_password(user, change_password.password)
            return self.success()
        except UserNotExistError:
            return self.not_found()

    async def get_by_id(self, request: Request):
        uid = request.path_params.get("uid") or request.user.identity
        user = await self._get_user(uid)
        return self.json(UserResponse(**user.dict()))

    async def change_status(self, request: Request):
        uid = request.path_params.get("uid")
        user = await self._get_user(uid)
        data = await request.json()
        schema = ChangeStatusRequest(**data)
        user = await self.user_service.change_status(user, schema.status)
        return self.json(UserResponse(**user.dict()))

    async def change_type(self, request: Request):
        uid = request.path_params.get("uid")
        user = await self._get_user(uid)
        data = await request.json()

        schema = ChangeTypeRequest(**data)
        user = await self.user_service.change_type(user, schema.type)
        return self.json(UserResponse(**user.dict()))

    async def search(self, request: Request):
        data = await request.json()
        user_request = UserSearchRequest(**data)
        usr_filter = (
            UserFilter(**user_request.filter.dict(skip_defaults=True))
            if user_request.filter
            else None
        )

        usr_sort = (
            UserSort(**user_request.sort.dict(skip_defaults=True)) if user_request.sort else None
        )

        usr_paginator = (
            Paginator(**user_request.paginator.dict(skip_defaults=True))
            if user_request.paginator
            else None
        )

        users, count = await self.user_service.search(usr_filter, usr_sort, usr_paginator)
        return self.json(
            UserSearchResponse(rows=(UserResponse(**u.dict()) for u in users), count=count)
        )

    async def auth(self, request: Request):
        data = await request.json()
        user_login = UserLoginRequest(**data)
        try:
            schema = LoginSchema(**user_login.dict())
            user = await self.user_service.auth(schema)
            return self._token_response(user)
        except UserNotExistError:
            return self.need_auth()

    async def refresh(self, request: Request):
        token = Token(token=request.cookies.get("RefreshToken"))
        try:
            payload = self.jwt_helper.decode(token.token)
            scopes = payload.get("scp") or []
            if SystemScopes.refresh not in scopes:
                return self.forbidden()
            user = await self.user_service.get_by_id(payload.get("sub"))
            return self._token_response(user)
        except Exception as e:  # TODO: Use upper level exception
            logger.exception(e)
            return self.forbidden()

    def _token_response(self, user):
        access_token, refresh_token = self._gen_token(user)
        response = self.json({"access_token": access_token, "refresh_token": refresh_token})
        expires = time() + self.security.jwt_cookie_expire
        response.set_cookie(
            self.security.jwt_cookie_key, access_token, httponly=True, expires=expires
        )
        response.set_cookie(
            self.security.jwt_cookie_refresh_key, refresh_token, httponly=True, expires=expires
        )
        return response

    def _gen_token(self, user: User) -> typing.Tuple[str, str]:
        access_token = self.jwt_helper.encode(
            {"sub": user.id, "exp": now().int_timestamp + self.token_expire, "scp": [user.role]}
        )
        refresh_token = self.jwt_helper.encode(
            {
                "sub": user.id,
                "exp": now().int_timestamp + self.refresh_token_expire,
                "scp": [SystemScopes.refresh],
            }
        )
        return access_token, refresh_token

    async def _get_user(self, uid: str) -> User:
        try:
            return await self.user_service.get_by_id(uid)
        except UserNotExistError:
            raise NotFoundError(f"User not found")
