from asyncpg import create_pool, Pool
from app.core.config import settings

_pool: Pool | None = None

async def get_pool() -> Pool:
    global _pool
    if _pool is None:
        _pool = await create_pool(dsn=settings.DATABASE_URL, min_size=5, max_size=20)
    return _pool

async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None