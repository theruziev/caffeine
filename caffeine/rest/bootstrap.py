import logging
from queue import LifoQueue
from typing import Optional

import sentry_sdk
from aio_pubsub.interfaces import PubSub
from fastapi import APIRouter, FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import LoggingIntegration

from caffeine import app_info
from caffeine.common.abc.bootstrap import BaseBootstrap
from caffeine.common.pubsub import PostgresPubSub
from caffeine.common.service.health.service import HealthService
from caffeine.common.service.user.service import UserService
from caffeine.common.settings import Settings
from caffeine.common.store.postgresql.db import PostgreSQLDb
from caffeine.common.store.postgresql.pubsub import PubSubStore
from caffeine.common.store.postgresql.user import PostgreSQLUserStore
from caffeine.common.template import Templater
from caffeine.rest.app.views import app_router
from caffeine.rest.users.views import user_router
from caffeine.rest.logger import logger
from caffeine.rest.utils.captcha import Recaptcha


class FastApiBootstrap(BaseBootstrap):
    def __init__(self, app, settings: Settings):
        self.app: FastAPI = app
        self.settings: Settings = settings
        self.db: PostgreSQLDb = PostgreSQLDb(str(self.settings.DB_DSN))
        self.shutdown_events = LifoQueue()
        self.pubsub: Optional[PubSub] = None
        self.states = {}

    async def init(self):
        await self.configure_server()
        if not self.settings.DEBUG and self.settings.SENTRY_URL:
            await self.init_sentry()
            logger.info("Sentry initialized.")
        await self.db.init()
        self.shutdown_events.put(self.db.shutdown)
        await self.init_caffeine()

        return self.app

    async def init_sentry(self):
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send errors as events
        )

        sentry_sdk.init(
            dsn=self.settings.SENTRY_URL,
            integrations=[sentry_logging],
            release=app_info.release_name,
        )

        self.app.add_middleware(SentryAsgiMiddleware)

    async def configure_server(self):
        self.app.debug = self.settings.DEBUG

    async def init_caffeine(self):
        recaptcha = self.states['recaptcha'] = Recaptcha(self.settings.RECAPTCHA_SECRET)
        self.shutdown_events.put(recaptcha.shutdown)
        templater = Templater(self.settings.TEMPLATE_PATH)
        # PubSub
        pubsub_store = PubSubStore(self.db)
        pubsub = PostgresPubSub(pubsub_store)
        # User
        user_store = PostgreSQLUserStore(self.db)
        self.states['user_service'] = UserService(self.settings, user_store, pubsub, templater)

        # App
        self.states['health_service'] = HealthService(self.db)

        # Routers
        api_router = APIRouter()
        api_router.include_router(app_router, prefix="/app", tags=['App'])
        api_router.include_router(user_router, prefix="/user", tags=['User'])
        self.app.include_router(api_router, prefix="/v1")
