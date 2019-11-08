import pytest
from asynctest import Mock
from starlette.applications import Starlette
from starlette.routing import Router
from starlette.testclient import TestClient
from urouter.exporters.starlette_exporter import StarletteRouter

from caffeine import app_info
from caffeine.common.service.health.service import HealthService
from caffeine.rest.handlers.app.handlers import AppHandler
from caffeine.rest.handlers.exception_handlers import ExceptionHandlers


@pytest.fixture
def app():
    def wrapper(health_service):
        app = Starlette()
        ExceptionHandlers(app)
        app_handler = AppHandler(health_service)
        router = StarletteRouter(app)

        def app_routes():
            app_router = router.make_router()
            app_router.get("/info", app_handler.app_info)
            app_router.get("/health", app_handler.health)
            return app_router
        router.mount("/v1/app", app_routes)
        router.export()

        return app

    return wrapper


@pytest.mark.parametrize("postgresql_connection", [True, False])
def test_register(app, postgresql_connection):
    health_service = Mock(HealthService(Mock()))

    async def side_effect():
        return {"postgresql_connection": postgresql_connection}

    health_service.check.side_effect = side_effect
    client = TestClient(app(health_service))

    response = client.get("v1/app/health")
    assert response.status_code == 200
    res = response.json()
    assert res.get("postgresql_connection") == postgresql_connection


def test_info(app):
    client = TestClient(app(Mock))

    response = client.get("v1/app/info")
    assert response.status_code == 200
    res = response.json()
    assert app_info.commit_hash == res["commit_hash"]
    assert app_info.release_name == res["release_name"]
    assert app_info.version == res["version"]
    assert app_info.name == res["name"]
