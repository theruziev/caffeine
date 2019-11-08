import logging
from queue import LifoQueue
from typing import Optional
import casbin
import sentry_sdk
from aio_pubsub.interfaces import PubSub
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import LoggingIntegration
from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from urouter.exporters.starlette_exporter import StarletteRouter

from caffeine import app_info
from caffeine.common.bootstrap import BaseBootstrap
from caffeine.common.pubsub import PostgresPubSub
from caffeine.common.security.casbin import Enforcer
from caffeine.common.security.jwt import JwtHelper
from caffeine.common.service.health.service import HealthService
from caffeine.common.service.user.service import UserService
from caffeine.common.settings import Settings
from caffeine.common.store.postgresql.db import PostgreSQLDb
from caffeine.common.store.postgresql.pubsub import PubSubStore
from caffeine.common.store.postgresql.user import PostgreSQLUserStore
from caffeine.common.template import Templater
from caffeine.rest.auth import JwtAuthBackend, need_auth
from caffeine.rest.handlers.app.handlers import AppHandler
from caffeine.rest.handlers.exception_handlers import ExceptionHandlers
from caffeine.rest.handlers.users.handlers import UserHandler
from caffeine.rest.logger import logger
from caffeine.rest.containers import SecurityContainer
from caffeine.rest.utils.captcha import Recaptcha


class WebBaseBootstrap(BaseBootstrap):
    def __init__(self, app, settings: Settings):
        self.app: Starlette = app
        self.settings: Settings = settings
        self.db: PostgreSQLDb = PostgreSQLDb(str(self.settings.DB_DSN))
        self.auth_backend: Optional[JwtAuthBackend] = None
        self.shutdown_events = LifoQueue()
        self.pubsub: Optional[PubSub] = None

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
        ExceptionHandlers(self.app)

    async def init_caffeine(self):
        jwt_helper = JwtHelper(str(self.settings.JWT_SECRET))
        e = casbin.Enforcer(self.settings.CASBIN_MODEL, self.settings.CASBIN_POLICY)
        enforcer = Enforcer(e)
        security_container = SecurityContainer(jwt_helper, enforcer)

        recaptcha = Recaptcha(self.settings.RECAPTCHA_SECRET)
        self.shutdown_events.put(recaptcha.shutdown)

        templater = Templater(self.settings.TEMPLATE_PATH)
        # PubSub
        pubsub_store = PubSubStore(self.db)
        pubsub = PostgresPubSub(pubsub_store)
        # User
        user_store = PostgreSQLUserStore(self.db)
        user_service = UserService(self.settings, user_store, pubsub, templater)
        user_handler = UserHandler(self.settings, user_service, security_container, recaptcha)

        # App
        health_service = HealthService(self.db)
        app_handler = AppHandler(health_service)

        auth_middleware = AuthenticationMiddleware(
            self.app, backend=JwtAuthBackend(user_service, security_container.jwt_helper)
        )
        router = StarletteRouter(self.app)
        public_router = router.make_router()
        private_router = router.make_router().use(auth_middleware)

        def user_routes():
            user_private_router = private_router.make_router()
            u = user_private_router.make_router()
            u.get("/{uid:str}/", need_auth(user_handler.get_by_id, ["admin"]))
            u.get("/{uid:str}/change_status", need_auth(user_handler.change_status, ["admin"]))
            u.get("/{uid:str}/change_type", need_auth(user_handler.change_type, ["admin"]))
            user_private_router.mount("/u", u)
            user_private_router.get("/me", need_auth(user_handler.get_by_id))

            user_public_router = router.make_router()
            user_public_router.post("/register", user_handler.register)
            user_public_router.get("/activate/{token:str}", user_handler.activate)
            user_public_router.post("/reset-password", user_handler.reset_password_request)
            user_public_router.get("/reset-password/{token:str}", user_handler.reset_password_check)
            user_public_router.post("/reset-password/{token:str}", user_handler.reset_password)
            user_public_router.post("/search", user_handler.search)
            user_public_router.post("/auth", user_handler.auth)
            user_public_router.post("/refresh", user_handler.refresh)

            user_router = router.make_router()
            user_router.mount("/user", user_public_router)
            user_router.mount("/user", user_private_router)
            return user_router

        def app_routes():
            app_router = public_router.make_router()
            app_router.get("/info", app_handler.app_info)
            app_router.get("/health", app_handler.health)
            return app_router

        router.mount("/v1", app_routes)
        router.mount("/v1", user_routes)
        router.export()
