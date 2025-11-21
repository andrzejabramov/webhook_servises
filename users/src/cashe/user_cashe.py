import json
from uuid import UUID
from asyncpg import Pool
from loguru import logger
from src.db.redis import redis
from src.utils.json_utils import maybe_json_dumps, maybe_json_loads
from src.exceptions.exceptions import UserNotFound
from src.schemas.users import UserDetailRead

CACHE_TTL_SECONDS = 600  # 10 минут

async def get_user_by_identifier_cached(identifier: str, pool: Pool) -> UserDetailRead:
    cache_key = f"user_by_id:{identifier}"
    cached = await redis.get(cache_key)
    if cached:
        logger.debug(f"Cache hit for identifier: {identifier}")
        data = json.loads(cached)
        data["profile"] = maybe_json_loads(data.get("profile"))
        return UserDetailRead(**data)

    # Запрос к БД через функцию
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM accounts.get_user_by_identifier_v1($1)",
            identifier
        )
        if not row:
            raise UserNotFound(user_id=identifier)

    user_dict = {
        "id": row["id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "is_active": row["is_active"],
        "profile": row["profile"],
        "groups": row["groups"],
        "contacts": row["contacts"],
    }

    # Кэшируем
    cache_data = user_dict.copy()
    cache_data["profile"] = maybe_json_dumps(cache_data["profile"])
    await redis.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(cache_data, default=str))
    logger.info(f"Cached user by identifier: {identifier}")
    return UserDetailRead(**user_dict)


async def invalidate_user_cache_by_id(user_id: UUID) -> None:
    """Инвалидация кэша по user_id (например, после PATCH)."""
    await redis.delete(f"user:{user_id}")
