from asyncpg import Pool, create_pool

from src.settings import settings

# Глобальные пулы (можно добавить другие: analytics_pool, auth_pool и т.д.)
_accounts_db_pool: Pool | None = None

async def init_pools():
    global _accounts_db_pool
    if _accounts_db_pool is None:
        _accounts_db_pool = await create_pool(dsn=str(settings.mydb_dsn))

async def close_pools():
    global _accounts_db_pool
    if _accounts_db_pool:
        await _accounts_db_pool.close()
        _accounts_db_pool = None

def get_accounts_db_pool() -> Pool:  # ← новая функция
    if _accounts_db_pool is None:
        raise RuntimeError("Accounts DB pool not initialized")
    return _accounts_db_pool