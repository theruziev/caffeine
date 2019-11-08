import pytest
from asynctest import MagicMock

from caffeine.common.pubsub import PostgresPubSub
from caffeine.common.store.postgresql.db import PostgreSQLDb
from caffeine.common.store.postgresql.pubsub import PubSubStore
from caffeine.common.test_utils.pubsub_store import gen_pubsub_msg


@pytest.fixture
async def db():
    db = PostgreSQLDb("dbname=postgres user=postgres host=127.0.0.1")
    await db.init()
    async with db.engine.acquire() as conn:
        await conn.execute("truncate table pubsub")
    yield db
    await db.shutdown()


@pytest.mark.asyncio
async def test_iteration_protocol():
    store = MagicMock(PubSubStore)
    msg = gen_pubsub_msg("a_chan")

    async def side_effect(x):
        assert x == msg

    store.add.side_effect = side_effect
    store.get_msg().__aenter__.return_value = msg
    pubsub = PostgresPubSub(store)
    subscriber = await pubsub.subscribe("a_chan")
    await pubsub.publish_raw_messages(msg)
    assert (await subscriber.__anext__()).data == msg.data


@pytest.mark.asyncio
async def test_pubsub():
    store = MagicMock(PubSubStore)
    msgs = [gen_pubsub_msg("a_chan") for _ in range(2)]
    store.get_msg().__aenter__.side_effect = msgs
    pubsub = PostgresPubSub(store)
    subscriber = await pubsub.subscribe("a_chan")
    await pubsub.publish("a_chan", msgs[0].data)
    await pubsub.publish("a_chan", msgs[1].data)
    assert (await subscriber.__anext__()).data == msgs[0].data
    assert (await subscriber.__anext__()).data == msgs[1].data
