from asyncpg import Pool
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.utils.json_utils import normalize_user_row, maybe_json_dumps, maybe_json_loads
from src.schemas.accounts import UserGroupMembershipCreate, UserGroupMembershipRead, UserGroupMembershipUpdate


class UserGroupMembershipService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def create(self, membership: UserGroupMembershipCreate) -> UserGroupMembershipRead:
        query = 'SELECT * FROM accounts.create_user_group_membership($1, $2)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, membership.user_id, membership.group_id)
        return UserGroupMembershipRead(**dict(row))

    async def get(self, user_id: UUID, group_id: int) -> Optional[UserGroupMembershipRead]:
        query = 'SELECT * FROM accounts.get_user_group_membership($1, $2)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id, group_id)
        return UserGroupMembershipRead(**dict(row)) if row else None

    async def get_user_groups(self, user_id: UUID, only_active: bool = True) -> List[UserGroupMembershipRead]:
        query = 'SELECT * FROM accounts.get_user_groups($1, $2)'
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, user_id, only_active)
        return [UserGroupMembershipRead(**dict(row)) for row in rows]

    async def deactivate(self, user_id: UUID, group_id: int) -> UserGroupMembershipRead:
        query = 'SELECT * FROM accounts.deactivate_user_group_membership($1, $2)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id, group_id)
        return UserGroupMembershipRead(**dict(row))

    async def reactivate(self, user_id: UUID, group_id: int) -> UserGroupMembershipRead:
        query = 'SELECT * FROM accounts.reactivate_user_group_membership($1, $2)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id, group_id)
        return UserGroupMembershipRead(**dict(row))


