import aioredis
from app.core.config import settings

_redis_client = None

async def get_redis_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            encoding="utf-8"
        )
    return _redis_client