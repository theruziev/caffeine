from caffeine.common.security.casbin import Enforcer
from caffeine.common.security.jwt import JwtHelper


class SecurityContainer:
    def __init__(self, jwt_helper: JwtHelper, enforcer: Enforcer):
        self.jwt_helper = jwt_helper
        self.enforcer = enforcer
