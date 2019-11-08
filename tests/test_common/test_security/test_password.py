from caffeine.common.security.password import bcrypt_hash, bcrypt_verify


def test_hash():
    h = bcrypt_hash("hello")
    h2 = bcrypt_hash("HELLO")
    assert h
    assert h2
    assert len(h) == 60
    assert len(h2) == 60
    assert h != h2


def test_verify():
    h = "$2y$12$Z9H9xG1ClLoRMYDgqeb3MusLlCAqJoSDm67OEcjIkUVE0T3eApx1m"
    assert bcrypt_verify("hello", h)
