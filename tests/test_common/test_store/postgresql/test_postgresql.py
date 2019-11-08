import pytest

from caffeine.common.store.postgresql.db import PostgreSQLDb


@pytest.mark.asyncio
async def test_connection():
    db = PostgreSQLDb("dbname=postgres user=postgres host=127.0.0.1")
    await db.init()
    async with db.engine.acquire() as conn:
        res = await conn.scalar("select 1")
        assert res == 1

    await db.shutdown()
