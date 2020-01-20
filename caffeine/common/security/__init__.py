import secrets


def generate_random(n: int) -> str:
    return secrets.token_hex(n)
