from time import time

from bson import ObjectId
from faker import Faker

from caffeine.common.store.goal import GoalStatusEnum, GoalTypeEnum, Goals

fake = Faker()


def gen_goal():
    data = {
        "id": str(ObjectId()),
        "user_id": str(ObjectId()),
        "name": fake.name(),
        "status": GoalStatusEnum.active,
        "type": GoalTypeEnum.default,
        "created_at": time(),
        "updated_at": time(),
    }

    return Goals(**data)
