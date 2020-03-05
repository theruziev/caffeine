from fastapi import APIRouter
from fastapi.params import Depends

from caffeine import app_info as info
from caffeine.common.service.health.service import HealthService
from caffeine.rest.dependencies import get_health_service

app_router = APIRouter()


@app_router.get("/health")
async def health(health_service: HealthService = Depends(get_health_service)):
    metrics = await health_service.check()
    return metrics


@app_router.get("/info")
async def app_info():
    return {
            "name": info.name,
            "release_name": info.release_name,
            "version": info.version,
            "commit_hash": info.commit_hash,
        }
