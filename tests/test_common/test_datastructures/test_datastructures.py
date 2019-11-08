from caffeine.common.datastructure.security import Secret


def test_secret():
    s = Secret("secret")
    assert repr(s) == "Secret('**********')"
    assert str(s) == "secret"
