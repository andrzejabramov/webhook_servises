from asyncpg import Pool
from src.schemas.accounts import UserGroupCreate, UserGroupUpdate, UserGroupRead
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