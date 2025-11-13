from asyncpg import Pool
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.utils.json_utils import normalize_user_row, maybe_json_dumps, maybe_json_loads
from src.schemas.accounts import UserContactCreate, UserContactRead


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
