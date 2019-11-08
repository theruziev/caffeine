from casbin import Enforcer as CasbinEnforcer


class Enforcer:
    def __init__(self, enforcer: CasbinEnforcer):
        self.enforcer = enforcer

    def enforce(self, sub, obj, act):
        return self.enforcer.enforce(sub, obj, act)
