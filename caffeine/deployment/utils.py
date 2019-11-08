from functools import wraps

from click import UsageError
from environs import Env


def dev_mode_only(fn):
    env = Env()
    env.read_env()

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not env.bool("DEBUG", False):
            raise UsageError("Command available only in dev mode")
        return fn(*args, **kwargs)

    return wrapper
