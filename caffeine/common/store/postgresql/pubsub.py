import pendulum
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from caffeine.common.store.postgresql.db import metadata, PostgreSQLDb
from caffeine.common.store.pubsub import PubSubMessage

pubsub_table = sa.Table(
    "pubsub",
    metadata,
    sa.Column("uuid", sa.String(36), index=True),
    sa.Column("channel", sa.String(256)),
    sa.Column("data", JSONB(), default=None, nullable=True),
    sa.Column("created_at", sa.Integer()),
    sa.Column("updated_at", sa.Integer()),
    sa.Column("is_done", sa.Boolean(), default=False),
)


class PubSubStore:
    def __init__(self, db: PostgreSQLDb):
        self.db = db

    async def add(self, *msgs: PubSubMessage):
        bulk = [
            {
                "uuid": m.uuid,
                "channel": m.channel,
                "data": m.data,
                "is_done": m.is_done,
                "created_at": m.created_at,
                "updated_at": m.updated_at,
            }
            for m in msgs
        ]

        q = pubsub_table.insert().values(bulk)
        async with self.db.engine.acquire() as conn:
            await conn.execute(q)

    async def get_msg(self, channel, batch=1):
        async with self.db.engine.acquire() as conn:
            q = (
                pubsub_table.select()
                .where(
                    sa.and_(pubsub_table.c.channel == channel, pubsub_table.c.is_done.is_(False))
                )
                .limit(batch)
                .with_for_update(skip_locked=True)
            )

            async with conn.begin():
                msg_db = await conn.execute(q)
                msgs = [self._make_msg(msg) async for msg in msg_db]
                if msgs:
                    yield msgs[0] if batch == 1 and msgs else msgs
                    make_done_msg_query = (
                        pubsub_table.update()
                        .values(updated_at=pendulum.now().int_timestamp, is_done=True)
                        .where(
                            (pubsub_table.c.uuid.in_([m.uuid for m in msgs]))
                            & (pubsub_table.c.is_done.is_(False))
                        )
                    )

                    await conn.execute(make_done_msg_query)

    @classmethod
    def _make_msg(cls, msg_db: dict) -> PubSubMessage:
        data = {
            "uuid": msg_db["uuid"],
            "channel": msg_db["channel"],
            "data": msg_db["data"],
            "created_at": msg_db["created_at"],
            "updated_at": msg_db["updated_at"],
            "is_done": msg_db["is_done"],
        }

        return PubSubMessage(**data)
