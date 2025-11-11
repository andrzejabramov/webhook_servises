from asyncpg import Pool
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.utils.json_utils import (
    normalize_user_row,
    maybe_json_dumps,
    maybe_json_loads,
)
from src.schemas.accounts import (
    UserGroupCreate,
    UserGroupUpdate,
    UserGroupRead,
    UserCreate,
    UserUpdate,
    UserRead,
    UserGroupMembershipCreate,
    UserGroupMembershipRead,
    UserGroupMembershipUpdate,
    UserContactCreate,
    UserContactRead,
)


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
        query = 'SELECT * FROM accounts.create_user($1::text, $2::jsonb)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                user.username,
                maybe_json_dumps(user.profile),
            )
        row_dict = dict(row)
        row_dict["profile"] = maybe_json_loads(row_dict.get("profile"))
        return UserRead(**normalize_user_row(row_dict))

    async def get_by_id(self, user_id: int) -> Optional[UserRead]:
        query = 'SELECT * FROM accounts.get_user($1)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id)
        return UserRead(**normalize_user_row(row)) if row else None

    async def get_all(self) -> List[UserRead]:
        query = 'SELECT * FROM accounts.list_users()'
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
        return [UserRead(**normalize_user_row(row)) for row in rows]

    async def update(
            self,
            user_id: UUID,
            is_active: Optional[bool] = None,
            profile: Optional[Dict[str, Any]] = None,
    ) -> UserRead:
        profile_json: Optional[str] = maybe_json_dumps(profile)
        query = 'SELECT * FROM accounts.update_user_profile($1, $2, $3)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                user_id,
                is_active,
                profile_json,
            )
        return UserRead(**normalize_user_row(row)) if row else None

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

class UserContactService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def create(self, contact: UserContactCreate) -> UserContactRead:
        query = 'SELECT * FROM accounts.create_user_contact($1, $2, $3)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, contact.user_id, contact.contact_type_id, contact.value)
        return UserContactRead(**dict(row))

    async def get_by_id(self, contact_id: UUID) -> Optional[UserContactRead]:
        query = 'SELECT * FROM accounts.get_user_contact_by_id($1)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, contact_id)
        return UserContactRead(**dict(row)) if row else None

    async def get_by_user_id(self, user_id: UUID, only_active: bool = True) -> List[UserContactRead]:
        query = 'SELECT * FROM accounts.get_user_contacts_by_user_id($1, $2)'
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, user_id, only_active)
        return [UserContactRead(**dict(row)) for row in rows]

    async def deactivate(self, contact_id: UUID) -> UserContactRead:
        query = 'SELECT * FROM accounts.deactivate_user_contact($1)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, contact_id)
        return UserContactRead(**dict(row))

    async def reactivate(self, contact_id: UUID) -> UserContactRead:
        query = 'SELECT * FROM accounts.reactivate_user_contact($1)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, contact_id)
        return UserContactRead(**dict(row))