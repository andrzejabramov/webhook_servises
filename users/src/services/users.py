from asyncpg import Pool
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.utils.json_utils import normalize_user_row, maybe_json_dumps, maybe_json_loads
from src.schemas.users import UserCreate, UserUpdate, UserRead


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


