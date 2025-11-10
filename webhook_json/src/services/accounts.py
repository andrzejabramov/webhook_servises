from asyncpg import Pool

from webhook_json.src.schemas.accounts import (
    UserGroupCreate,
    UserGroupUpdate,
    UserGroupRead,
    UserCreate,
    UserUpdate,
    UserRead
)
from typing import List, Optional
import uuid

class UserGroupService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def create(self, group: UserGroupCreate) -> UserGroupRead:
        query = 'SELECT * FROM accounts.create_user_group($1, $2)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, group.name, group.description)
        return UserGroupRead(**dict(row))

    async def get_all(self) -> List[UserGroupRead]:
        query = 'SELECT * FROM accounts.list_user_groups()'
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
        return [UserGroupRead(**dict(row)) for row in rows]

    async def update(self, group_id: int, group: UserGroupUpdate) -> Optional[UserGroupRead]:
        query = 'SELECT * FROM accounts.update_user_group($1, $2, $3, $4)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                group_id,
                group.name,  # может быть None
                group.description,  # может быть None
                group.is_active  # может быть None
            )
        return UserGroupRead(**dict(row)) if row else None


class UserService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def create(self, user: UserCreate) -> UserRead:
        query = 'SELECT * FROM accounts.create_user($1, $2)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user.email, user.full_name)
        return UserRead(**dict(row))

    async def get_by_id(self, user_id: int) -> Optional[UserRead]:
        query = 'SELECT * FROM accounts.get_user($1)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id)
        return UserRead(**dict(row)) if row else None

    async def get_all(self) -> List[UserRead]:
        query = 'SELECT * FROM accounts.list_users()'
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
        return [UserRead(**dict(row)) for row in rows]

    async def update(self, user_id: int, user_update: UserUpdate) -> Optional[UserRead]:
        query = 'SELECT * FROM accounts.update_user($1, $2, $3, $4)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                user_id,
                user_update.email,
                user_update.full_name,
                user_update.is_active
            )
        return UserRead(**dict(row)) if row else None