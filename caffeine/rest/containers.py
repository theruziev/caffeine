from caffeine.common.security.casbin import Enforcer
from caffeine.common.security.jwt import JwtHelper


class SecurityContainer:
    def __init__(self, jwt_helper: JwtHelper, enforcer: Enforcer, jwt_cookie_key: str, jwt_cookie_refresh_key: str,
                 jwt_cookie_expire: int):
        self.jwt_helper = jwt_helper
        self.enforcer = enforcer
        self.jwt_cookie_key = jwt_cookie_key
        self.jwt_cookie_refresh_key = jwt_cookie_refresh_key
        self.jwt_cookie_expire = jwt_cookie_expire
