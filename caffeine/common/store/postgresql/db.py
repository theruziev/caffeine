import typing

import sqlalchemy as sa
from aiopg.sa import Engine, create_engine

metadata = sa.MetaData()


class DoesNotExistException(Exception):
    pass


class PostgreSQLDb:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.engine: typing.Optional[Engine] = None

    async def init(self):
        self.engine = await create_engine(self.dsn)

    async def shutdown(self):
        self.engine.terminate()
        await self.engine.wait_closed()
