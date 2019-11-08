import secrets
from time import time

from faker import Faker

from caffeine.common.security.password import bcrypt_hash
from caffeine.common.store.user import UserStatusEnum, UserTypeEnum, User

fake = Faker()


def gen_user(id_is_empty=False):
    data = {
        "email": fake.email(),
        "password": bcrypt_hash(fake.password()),
        "status": UserStatusEnum.active.value,
        "type": UserTypeEnum.default.value,
        "created_at": time(),
        "updated_at": time(),
    }
    if id_is_empty:
        data["id"] = secrets.randbelow(1000000)

    return User(**data)
