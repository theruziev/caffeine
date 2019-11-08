import typing
from time import time
from uuid import uuid4

from aio_pubsub.interfaces import Subscriber, PubSub

from caffeine.common.store.postgresql.pubsub import PubSubStore
from caffeine.common.store.pubsub import PubSubMessage


class PubSubSubscriber(Subscriber):
    def __init__(self, channel, store: PubSubStore, batch=1):
        self.channel = channel
        self.store = store
        self.batch = batch

    def __aiter__(self):
        return self

    async def __anext__(self):
        while True:
            async with self.store.get_msg(self.channel, batch=self.batch) as msg:
                if msg:
                    return msg


class PostgresPubSub(PubSub):
    def __init__(self, store: PubSubStore):
        self.store = store

    async def publish(self, channel: typing.Any, message: typing.Any):
        msg = PubSubMessage(
            uuid=str(uuid4()), channel=channel, data=message, created_at=time(), updated_at=time()
        )
        await self.publish_raw_messages(msg)

    async def publish_raw_messages(self, *msgs):
        await self.store.add(*msgs)

    async def subscribe(self, channel: typing.Any):
        return PubSubSubscriber(channel, self.store)
