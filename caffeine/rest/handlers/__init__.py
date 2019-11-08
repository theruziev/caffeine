from abc import ABCMeta, abstractmethod
from typing import Type, TypeVar, Union, Any

from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.routing import Route

T = TypeVar("T")


class NotFoundError(Exception):
    pass


class RegisterRouter(metaclass=ABCMeta):
    @abstractmethod
    def init_router(self) -> Route:
        pass  # pragma: no cover


class Handler(metaclass=ABCMeta):
    @classmethod
    def error_message(cls, msg, status_code):
        return JSONResponse({"error": msg}, status_code=status_code)

    @classmethod
    def not_found(cls):
        return JSONResponse(status_code=404)

    @classmethod
    def forbidden(cls):
        return JSONResponse(status_code=403)

    @classmethod
    def need_auth(cls):
        return JSONResponse(status_code=401)

    @classmethod
    def success(cls):
        return JSONResponse({"success": True})

    @classmethod
    def json(cls, data: Union[Any, Type[BaseModel]], status_code=200):
        if isinstance(data, BaseModel):
            data = data.dict()
        return JSONResponse(data, status_code=status_code)
