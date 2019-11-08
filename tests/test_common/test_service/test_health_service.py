import pytest
from asynctest import Mock, MagicMock

from caffeine.common.service.health.service import HealthService
from caffeine.common.store.postgresql.db import PostgreSQLDb


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_res, res", [(True, True), (True, True), (False, False)])
async def test_health_postgres_connection(mock_res, res):
    """

    :param mock_res:
    :param res:
    :return:
    """
    postgres = MagicMock(PostgreSQLDb(""))

    class EngineMock:
        async def execute(self, *args, **kwargs):
            if not mock_res:
                raise Exception("blah fake exception")
            return mock_res

    postgres.engine.acquire().__aenter__.return_value = EngineMock
    postgres.engine.acquire().__aexit__.return_value = None
    health_service = HealthService(postgres)
    assert await health_service.postgres_connection_check() == res
