from caffeine.common.security import generate_random


def test_random_generator():
    s = generate_random(10)
    assert s
    assert len(s) == 20
