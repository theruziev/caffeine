import casbin

from caffeine.common.security.casbin import Enforcer


def test_enforcer(static_dir):
    enforcer = casbin.Enforcer(f"{static_dir}/casbin/model.conf", f"{static_dir}/casbin/policy.csv")
    my_enforcer = Enforcer(enforcer)
    assert my_enforcer.enforce("alice", "data1", "read")
    assert not my_enforcer.enforce("test", "data1", "read")
