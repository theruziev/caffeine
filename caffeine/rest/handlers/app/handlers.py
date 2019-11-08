from starlette.requests import Request

from caffeine import app_info
from caffeine.common.service.health.service import HealthService
from caffeine.rest.handlers import Handler


class AppHandler(Handler):
    def __init__(self, health_service: HealthService):
        self.health_service = health_service

    async def health(self, request: Request):
        metrics = await self.health_service.check()
        return self.json(metrics)

    async def app_info(self, request: Request):
        return self.json(
            {
                "name": app_info.name,
                "release_name": app_info.release_name,
                "version": app_info.version,
                "commit_hash": app_info.commit_hash,
            }
        )
