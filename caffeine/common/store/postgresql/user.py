from typing import Tuple, List

import sqlalchemy as sa
from sqlalchemy import exists, select, func, and_

from caffeine.common.store import Paginator
from caffeine.common.store.postgresql.db import metadata, DoesNotExistException, PostgreSQLDb
from caffeine.common.store.user import UserStore, UserFilter, UserSort, User

user_table = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("email", sa.String(256), unique=True, index=True),
    sa.Column("password", sa.String(256), nullable=False),
    sa.Column("status", sa.String(256)),
    sa.Column("type", sa.String(256)),
    sa.Column("role", sa.String(256)),
    sa.Column("activation_code", sa.String(1024), nullable=True, default=None),
    sa.Column("reset_password_code", sa.String(256), nullable=True, default=None),
    sa.Column("created_at", sa.Integer),
    sa.Column("updated_at", sa.Integer),
    sa.Column("ref_id", sa.Integer, nullable=True, default=None),
)


class PostgreSQLUserFilter:
    def __init__(self, user_filter: UserFilter):
        self.user_filter = user_filter

    def prepare(self):
        conditions = []
        if not self.user_filter:
            return and_(*conditions)

        if self.user_filter.id:
            conditions.append(user_table.c.id == self.user_filter.id)
        if self.user_filter.email:
            conditions.append(user_table.c.email.like(self.user_filter.email))
        if self.user_filter.created_at_from:
            conditions.append(user_table.c.created_at >= self.user_filter.created_at_from)
        if self.user_filter.created_at_to:
            conditions.append(user_table.c.created_at < self.user_filter.created_at_to)
        if self.user_filter.status:
            conditions.append(user_table.c.status == self.user_filter.status)
        if self.user_filter.type:
            conditions.append(user_table.c.type == self.user_filter.type)
        return and_(*conditions)


class PostgresSQLUserSort:
    def __init__(self, sort: UserSort):
        self.sort = sort

    def prepare(self):
        sorting = []
        if self.sort and self.sort.id != 0:
            sorting.append(user_table.c.id.asc() if self.sort.id == 1 else user_table.c.id.desc())

        if self.sort and self.sort.email != 0:
            sorting.append(
                user_table.c.email.asc() if self.sort.email == 1 else user_table.c.email.desc()
            )

        if self.sort and self.sort.type != 0:
            sorting.append(
                user_table.c.type.asc() if self.sort.type == 1 else user_table.c.type.desc()
            )

        if self.sort and self.sort.created_at != 0:
            sorting.append(
                user_table.c.created_at.asc()
                if self.sort.created_at == 1
                else user_table.c.created_at.desc()
            )

        return sorting


class PostgreSQLUserStore(UserStore):
    def __init__(self, db: PostgreSQLDb):
        self.db = db

    async def add(self, user: User) -> User:
        q = user_table.insert().values(
            email=user.email,
            status=user.status,
            password=user.password,
            type=user.type,
            role=user.role,
            activation_code=user.activation_code,
            reset_password_code=user.reset_password_code,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        async with self.db.engine.acquire() as conn:
            user.id = await conn.scalar(q)
        return user

    async def update(self, user: User) -> User:
        q = (
            user_table.update()
            .values(
                email=user.email,
                password=user.password,
                status=user.status,
                type=user.type,
                role=user.role,
                activation_code=user.activation_code,
                reset_password_code=user.reset_password_code,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            .where(user_table.c.id == user.id)
        )
        async with self.db.engine.acquire() as conn:
            await conn.execute(q)
        return user

    async def find_by_id(self, uid: int) -> User:
        q = user_table.select().where(user_table.c.id == uid)
        async with self.db.engine.acquire() as conn:
            res = await conn.execute(q)

            user_db = await res.fetchone()
            if not user_db:
                raise DoesNotExistException(f"User with id: {uid} doesn't exist.")

            return self._make_user(user_db)

    async def find_by_email(self, email: str) -> User:
        q = user_table.select().where(user_table.c.email == email)
        async with self.db.engine.acquire() as conn:
            res = await conn.execute(q)

            user_db = await res.fetchone()
            if not user_db:
                raise DoesNotExistException(f"User with email: {email} doesn't exist.")

            return self._make_user(user_db)

    async def exist_by_email(self, email: str) -> bool:
        async with self.db.engine.acquire() as conn:
            return await conn.scalar(select([exists().where(user_table.c.email == email)]))

    async def find_by_activation_code(self, activation_code: str) -> User:
        q = user_table.select().where(user_table.c.activation_code == activation_code)
        async with self.db.engine.acquire() as conn:
            res = await conn.execute(q)

            user_db = await res.fetchone()
            if not user_db:
                raise DoesNotExistException(
                    f"User with activation_code: {activation_code} doesn't exist."
                )

            return self._make_user(user_db)

    async def find_by_reset_password_code(self, reset_password_code: str) -> User:
        q = user_table.select().where(user_table.c.reset_password_code == reset_password_code)
        async with self.db.engine.acquire() as conn:
            res = await conn.execute(q)

            user_db = await res.fetchone()
            if not user_db:
                raise DoesNotExistException(
                    f"User with reset_password_code: {reset_password_code} does'nt exist."
                )

            return self._make_user(user_db)

    async def search(
        self, usr_filter: UserFilter = None, sort: UserSort = None, paginator: Paginator = None
    ) -> Tuple[List[User], int]:

        postgres_usr_filter = PostgreSQLUserFilter(usr_filter)
        condition = postgres_usr_filter.prepare()

        count_query = select([func.count(user_table.c.id)]).where(condition)
        async with self.db.engine.acquire() as conn:
            count = await conn.scalar(count_query)
        select_query = user_table.select().where(condition)

        postgres_user_sort = PostgresSQLUserSort(sort)
        sorting = postgres_user_sort.prepare()
        if sorting:
            select_query = select_query.order_by(*sorting)

        if paginator:
            select_query = select_query.limit(paginator.per_page).offset(
                (paginator.page - 1) * paginator.per_page
            )
        async with self.db.engine.acquire() as conn:
            users_db = await conn.execute(select_query)
            return [self._make_user(r) async for r in users_db], count

    @classmethod
    def _make_user(cls, user_db):
        data = {
            "id": user_db["id"],
            "email": user_db["email"],
            "password": user_db["password"],
            "status": user_db["status"],
            "type": user_db["type"],
            "role": user_db["role"],
            "activation_code": user_db["activation_code"],
            "reset_password_code": user_db["reset_password_code"],
            "created_at": user_db["created_at"],
            "updated_at": user_db["updated_at"],
        }

        return User(**data)
