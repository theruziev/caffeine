from time import time

import pytest
from jwt import ExpiredSignatureError, InvalidSignatureError

from caffeine.common.security.jwt import JwtHelper

jwt_res = (
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2M"
    "jM5MDIyfQ._rekuE9zS7P3yjHiM60h5Ukc2T4Xsq8lB5FH6sDHkKY"
)
data = {"sub": "1234567890", "name": "John Doe", "iat": 1516239022}
jwt = JwtHelper("SECRET")


def test_encode():
    jwt_other = JwtHelper("SECRET2")

    res = jwt.encode(data)
    assert res == jwt_res

    assert jwt_other.encode(data) != res


def test_decode():
    jwt_other = JwtHelper("SECRET2")

    res = jwt.decode(jwt_res)
    assert res == data

    with pytest.raises(InvalidSignatureError):
        assert jwt_other.decode(jwt_res)


def test_jwt_expire():
    exp_data = {"exp": time() - 5}
    res_jwt = jwt.encode(exp_data)
    with pytest.raises(ExpiredSignatureError):
        jwt.decode(res_jwt)
