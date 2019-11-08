import typing

import jwt


class JwtHelper:
    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm

    def encode(self, data: dict, headers: typing.Optional[dict] = None) -> str:
        return jwt.encode(data, self.secret, self.algorithm, headers).decode()

    def decode(self, s: str, verify: bool = True, options: typing.Optional[dict] = None) -> dict:
        return jwt.decode(
            s, self.secret, algorithms=[self.algorithm], verify=verify, options=options
        )
