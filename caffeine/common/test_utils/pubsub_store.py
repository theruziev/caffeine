from time import time
from uuid import uuid4

from faker import Faker

from caffeine.common.store.pubsub import PubSubMessage

fake = Faker()


def gen_pubsub_msg(channel):
    data = {
        "uuid": str(uuid4()),
        "channel": channel,
        "is_done": False,
        "data": {"hello": "world"},
        "created_at": int(time()),
        "updated_at": int(time()),
    }

    return PubSubMessage(**data)
