import secrets


def generate_random(n):
    return secrets.token_hex(n)
