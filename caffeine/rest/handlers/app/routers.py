from urouter.exporters.starlette_exporter import StarletteRouter
from caffeine.rest.handlers.app.handlers import AppHandler


class AppRouter:
    def __init__(self, app_handler: AppHandler, router: StarletteRouter):
        self.app_handler = app_handler
        self.router = router

    def init(self):
        router = self.router.make_router()
        router.get("/info", self.app_handler.app_info)
        router.get("/health", self.app_handler.health)
        return router
