from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Tuple, List

from pendulum import now
from pydantic import BaseModel, EmailStr

from caffeine.common.store import Paginator


class UserRoleEnum(str, Enum):
    user = "user"
    admin = "admin"


class UserStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    register = "register"


class UserTypeEnum(str, Enum):
    default = "default"
    gdpr_removed = "gdpr_removed"


class User(BaseModel):
    id: int = None
    email: EmailStr
    password: str
    status: UserStatusEnum = UserStatusEnum.register
    type: UserTypeEnum = UserTypeEnum.default
    role: UserRoleEnum = UserRoleEnum.user
    activation_code: str = None
    reset_password_code: str = None
    created_at: int
    updated_at: int
    ref_id: int = None

    def touch(self):
        self.updated_at = now().int_timestamp


class UserSort(BaseModel):
    id: int = 0
    email: int = 0
    type: int = 0
    created_at: int = 0


class UserFilter(BaseModel):
    id: int = None
    email: str = None
    status: UserStatusEnum = None
    type: UserTypeEnum = None
    created_at_from: int = None
    created_at_to: int = None
    ref_id: int = None


class UserStore(metaclass=ABCMeta):
    @abstractmethod
    async def add(self, user: User) -> User:
        pass  # pragma: no cover

    @abstractmethod
    async def update(self, user: User) -> User:
        pass  # pragma: no cover

    @abstractmethod
    async def find_by_id(self, uid: str) -> User:
        pass  # pragma: no cover

    @abstractmethod
    async def find_by_email(self, email: str) -> User:
        pass  # pragma: no cover

    @abstractmethod
    async def exist_by_email(self, email: str) -> User:
        pass  # pragma: no cover

    @abstractmethod
    async def find_by_activation_code(self, activation_code: str) -> User:
        pass  # pragma: no cover

    @abstractmethod
    async def find_by_reset_password_code(self, reset_password_code: str) -> User:
        pass  # pragma: no cover

    @abstractmethod
    async def search(
        self, usr_filter: UserFilter = None, sort: UserSort = None, paginator: Paginator = None
    ) -> Tuple[List[User], int]:
        pass  # pragma: no cover
