from caffeine.common.logger import logger
from caffeine.common.store.postgresql.db import PostgreSQLDb


class HealthService:
    def __init__(self, db: PostgreSQLDb):
        self.db = db

    async def check(self) -> dict:
        res = {"postgresql_connection": await self.postgres_connection_check()}

        return res

    async def postgres_connection_check(self) -> bool:
        try:
            async with self.db.engine.acquire() as conn:
                await conn.execute("SELECT 1;")
                return True
        except Exception as e:
            logger.exception(e)

        return False
