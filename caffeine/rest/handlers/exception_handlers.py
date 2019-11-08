from json import JSONDecodeError

from pydantic.error_wrappers import ValidationError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse

from caffeine.rest.handlers import NotFoundError


class ExceptionHandlers:
    def __init__(self, app: Starlette):
        self.app = app
        self.app.add_exception_handler(JSONDecodeError, self.bad_request)
        self.app.add_exception_handler(ValidationError, self.validation_error)
        self.app.add_exception_handler(NotFoundError, self.not_found)

    @classmethod
    async def bad_request(cls, request: Request, exc):
        return JSONResponse(status_code=400)

    @classmethod
    async def validation_error(cls, request: Request, exc: ValidationError):
        return JSONResponse(exc.errors(), status_code=400)

    @classmethod
    async def not_found(cls, request, exc):
        return JSONResponse({"error": str(exc)}, status_code=404)
