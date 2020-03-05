from starlette.requests import Request

from caffeine.common.service.health.service import HealthService
from caffeine.common.service.user.service import UserService
from caffeine.rest.utils.captcha import Recaptcha


def get_user_service(request: Request) -> UserService:
    return request.state.user_service


def get_health_service(request: Request) -> HealthService:
    return request.state.health_service


def get_recaptcha(request: Request) -> Recaptcha:
    return request.state.recaptcha
