from typing import List

from pydantic import BaseModel, EmailStr

from caffeine.common.schema import PasswordStr
from caffeine.common.store import SortInt
from caffeine.common.store.user import UserStatusEnum, UserTypeEnum
from caffeine.rest.schemas import Paginator


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: PasswordStr


class Token(BaseModel):
    token: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: PasswordStr
    captcha: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    captcha: str


class ChangePasswordRequest(BaseModel):
    password: PasswordStr


class ChangeStatusRequest(BaseModel):
    status: UserStatusEnum


class ChangeTypeRequest(BaseModel):
    type: UserTypeEnum


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: int
    updated_at: int
    status: UserStatusEnum
    type: UserTypeEnum


# Search
class UserSearchResponse(BaseModel):
    rows: List[UserResponse] = []
    count: int = 0


class UserSearchFilter(BaseModel):
    id: int = None
    email: str = None
    status: UserStatusEnum = None
    type: UserTypeEnum = None
    created_at_from: int = None
    created_at_to: int = None


class UserSearchSort(BaseModel):
    id: SortInt = 0
    email: SortInt = 0
    type: SortInt = 0
    created_at: SortInt = 0


class UserSearchRequest(BaseModel):
    filter: UserSearchFilter = None
    paginator: Paginator = None
    sort: UserSearchSort = None
