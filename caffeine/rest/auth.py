from enum import Enum

from starlette.authentication import (
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
    AuthCredentials,
    requires,
)

from caffeine.common.security.jwt import JwtHelper
from caffeine.common.service.user.service import UserService


class SystemScopes(str, Enum):
    authenticated = "authenticated"
    refresh = "refresh"


def need_auth(fn, scopes=None):
    scopes = scopes or []
    return requires([SystemScopes.authenticated] + scopes)(fn)


class User(SimpleUser):
    def __init__(self, username, uid, payload=None):
        super(User, self).__init__(username)
        self.uid = uid
        self.payload = payload

    @property
    def identity(self) -> str:
        return self.uid


class JwtAuthBackend(AuthenticationBackend):
    def __init__(self, user_service: UserService, jwt_helper: JwtHelper):
        self.user_service = user_service
        self.jwt_helper = jwt_helper

    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            return

        auth = request.headers["Authorization"]
        try:
            scheme, token = auth.split()
            if scheme.lower() != "bearer":
                return
            data = self.jwt_helper.decode(token)
            user = await self.user_service.get_by_id(data.get("sub"))
            scopes = data.get("scp", [])
            if SystemScopes.refresh in scopes:
                return

            return (
                AuthCredentials(scopes + [SystemScopes.authenticated]),
                User(user.email, user.id, data),
            )
        except (ValueError, UnicodeDecodeError, Exception):
            raise AuthenticationError("Invalid bearer auth credentials")
