from passlib.hash import bcrypt


def bcrypt_hash(s: str) -> str:
    return bcrypt.hash(s)


def bcrypt_verify(s: str, h: str) -> bool:
    return bcrypt.verify(s, h)
