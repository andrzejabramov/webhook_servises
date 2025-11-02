from asyncpg import Pool, create_pool
from src.settings import settings

# Глобальные пулы (можно добавить другие: analytics_pool, auth_pool и т.д.)
_main_db_pool: Pool | None = None

async def init_main_db_pool():
    global _main_db_pool
    if _main_db_pool is None:
        _main_db_pool = await create_pool(dsn=settings.database_url)

async def close_main_db_pool():
    global _main_db_pool
    if _main_db_pool:
        await _main_db_pool.close()
        _main_db_pool = None

def get_main_db_pool() -> Pool:
    if _main_db_pool is None:
        raise RuntimeError("Main DB pool not initialized")
    return _main_db_pool