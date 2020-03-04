from starlette.middleware.authentication import AuthenticationMiddleware
from urouter.exporters.starlette_exporter import StarletteRouter

from caffeine.rest.auth import need_auth
from caffeine.rest.handlers.users.handlers import UserHandler


class UserRouter:
    def __init__(
        self,
        user_handler: UserHandler,
        auth_middleware: AuthenticationMiddleware,
        router: StarletteRouter,
    ):
        self.user_handler = user_handler
        self.auth_middleware = auth_middleware
        self.router = router

    def init(self):
        user_private_router = self.router.make_router().use(self.auth_middleware)
        u = self.router.make_router()
        u.get("/{uid:str}/", need_auth(self.user_handler.get_by_id, ["admin"]))
        u.post("/{uid:str}/change_status", need_auth(self.user_handler.change_status, ["admin"]))
        u.post("/{uid:str}/change_type", need_auth(self.user_handler.change_type, ["admin"]))

        user_private_router.mount("/u", u)
        user_private_router.get("/me", need_auth(self.user_handler.get_by_id))

        user_public_router = self.router.make_router()
        user_public_router.post("/register", self.user_handler.register)
        user_public_router.get("/activate/{token:str}", self.user_handler.activate)
        user_public_router.post("/reset-password", self.user_handler.reset_password_request)
        user_public_router.get(
            "/reset-password/{token:str}", self.user_handler.reset_password_check
        )
        user_public_router.post("/reset-password/{token:str}", self.user_handler.reset_password)
        user_public_router.post("/search", self.user_handler.search)
        user_public_router.get("/refresh", self.user_handler.refresh)
        user_public_router.post("/auth", self.user_handler.auth)

        user_router = self.router.make_router()
        user_router.mount("/user", user_public_router)
        user_router.mount("/user", user_private_router)
        return user_router
