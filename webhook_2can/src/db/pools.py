from asyncpg import Pool, create_pool

from src.settings import settings


write_pool: Pool
read_pool: Pool

async def init_pools():
    global write_pool, read_pool
    write_pool = await create_pool(str(settings.database_write_url))
    read_pool = await create_pool(str(settings.database_read_url))

async def close_pools():
    await write_pool.close()
    await read_pool.close()

# Зависимости для роутов
def get_write_pool() -> Pool:
    return write_pool

def get_read_pool() -> Pool:
    return read_pool
