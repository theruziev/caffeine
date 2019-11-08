import pytest

from caffeine.common.store.postgresql.db import PostgreSQLDb
from caffeine.common.store.postgresql.pubsub import PubSubStore
from caffeine.common.test_utils.pubsub_store import gen_pubsub_msg


@pytest.fixture
async def db():
    db = PostgreSQLDb("dbname=postgres user=postgres host=127.0.0.1")
    await db.init()
    async with db.engine.acquire() as conn:
        await conn.execute("truncate table pubsub;")
    yield db
    await db.shutdown()


@pytest.mark.asyncio
@pytest.mark.db
async def test_add(db):
    store = PubSubStore(db)
    await store.add(gen_pubsub_msg("test_channel"))
    await store.add(*[gen_pubsub_msg("test_channel") for r in range(1000)])


@pytest.mark.asyncio
@pytest.mark.db
async def test_get_msg(db):
    store = PubSubStore(db)
    new_msgs = [gen_pubsub_msg("test_channel") for r in range(5)]
    uuids = [m.uuid for m in new_msgs]
    await store.add(*new_msgs)
    async with store.get_msg("test_channel", 10) as msg:
        for m in msg:
            assert m.uuid in uuids
