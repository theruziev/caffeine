import pytest
from faker import Faker

from caffeine.common.store import Paginator
from caffeine.common.store.postgresql.user import PostgreSQLUserStore
from caffeine.common.store.postgresql.db import DoesNotExistException, PostgreSQLDb
from caffeine.common.store.user import UserFilter, UserSort
from caffeine.common.test_utils.user_store import gen_user

fake = Faker()


@pytest.fixture
async def db():
    db = PostgreSQLDb("dbname=postgres user=postgres host=127.0.0.1")
    await db.init()
    yield db
    await db.shutdown()


@pytest.mark.asyncio
@pytest.mark.db
async def test_add(db):
    store = PostgreSQLUserStore(db)

    user = await store.add(gen_user())
    assert user.id


@pytest.mark.asyncio
@pytest.mark.db
async def test_update(db):
    store = PostgreSQLUserStore(db)

    user = await store.add(gen_user())
    assert user.id

    user.password = "Password$12"
    await store.update(user)
    updated_user = await store.find_by_id(user.id)
    assert updated_user.password == user.password


@pytest.mark.asyncio
@pytest.mark.db
async def test_find_by_id(db):
    store = PostgreSQLUserStore(db)

    user = await store.add(gen_user())
    assert user.id

    find_user = await store.find_by_id(user.id)
    assert user.email == find_user.email

    with pytest.raises(DoesNotExistException):
        await store.find_by_id(-5)


@pytest.mark.asyncio
@pytest.mark.db
async def test_find_by_email(db):
    store = PostgreSQLUserStore(db)

    user = await store.add(gen_user())
    assert user.id

    find_user = await store.find_by_email(user.email)
    assert user.email == find_user.email

    with pytest.raises(DoesNotExistException):
        await store.find_by_email(fake.sha256(raw_output=False))


@pytest.mark.asyncio
@pytest.mark.db
async def test_exist_by_email(db):
    store = PostgreSQLUserStore(db)

    user = await store.add(gen_user())
    assert user.id

    n = await store.exist_by_email(user.email)
    assert n

    assert await store.exist_by_email(fake.sha256(raw_output=False)) is False


@pytest.mark.asyncio
@pytest.mark.db
async def test_find_by_activation_code(db):
    store = PostgreSQLUserStore(db)
    u = gen_user()
    u.activation_code = fake.sha256(raw_output=False)
    user = await store.add(u)
    assert user.id
    assert user.activation_code == u.activation_code

    find_user = await store.find_by_activation_code(user.activation_code)
    assert user.activation_code == find_user.activation_code

    with pytest.raises(DoesNotExistException):
        await store.find_by_activation_code(fake.sha256(raw_output=False))


@pytest.mark.asyncio
@pytest.mark.db
async def test_find_by_reset_password_code(db):
    store = PostgreSQLUserStore(db)
    u = gen_user()
    u.reset_password_code = fake.sha256(raw_output=False)
    user = await store.add(u)
    assert user.id
    assert user.reset_password_code == u.reset_password_code

    find_user = await store.find_by_reset_password_code(user.reset_password_code)
    assert user.reset_password_code == find_user.reset_password_code

    with pytest.raises(DoesNotExistException):
        await store.find_by_reset_password_code(fake.sha256(raw_output=False))


@pytest.mark.asyncio
@pytest.mark.db
async def test_search_user(db):
    store = PostgreSQLUserStore(db)
    users, cnt = await store.search()
    async with db.engine.acquire() as conn:
        correct_count = await conn.scalar("select count(*) from users")
        assert len(users) == correct_count
        assert cnt == correct_count
    # Filter
    user = await store.add(gen_user())
    assert user.id
    usr_filter = UserFilter(**{"email": user.email})
    users, cnt = await store.search(usr_filter)
    assert cnt == 1
    assert len(users) == 1
    assert users[0] == user

    # Sorting
    users, cnt = await store.search(sort=UserSort(email=1))
    async with db.engine.acquire() as conn:
        correct_sorted_users_res = await conn.execute("select email from users order by email")
        correct_sorted_users = [u.email async for u in correct_sorted_users_res]
        assert correct_sorted_users == [u.email for u in users]

    # Pagination
    users, cnt = await store.search(sort=UserSort(email=1), paginator=Paginator(page=1, per_page=2))
    assert len(users) == 2
    assert [u.email for u in users] == correct_sorted_users[:2]
