from app.db.pool import get_pool
from app.redis.client import get_redis

async def get_db_pool():
    return await get_pool()

async def get_redis_client():
    return await get_redis()