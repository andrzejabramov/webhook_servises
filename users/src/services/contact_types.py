from asyncpg import Pool
from typing import List

from src.utils.json_utils import normalize_user_row, maybe_json_dumps, maybe_json_loads
from src.schemas.contact_types import ContactTypeCreate, ContactTypeRead


class ContactTypeService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def list_all(self) -> List[ContactTypeRead]:
        query = 'SELECT * FROM accounts.list_contact_types()'
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
        return [ContactTypeRead(**dict(row)) for row in rows]

    async def create(self, data: ContactTypeCreate) -> ContactTypeRead:
        query = 'SELECT * FROM accounts.create_contact_type($1)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, data.name)
        return ContactTypeRead(**dict(row))
