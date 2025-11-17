from datetime import datetime, timezone, timedelta
from asyncpg import Record
import json

from app.core.config import settings
from app.utils.security import hash_password, create_refresh_token as gen_refresh_token
from app.db.pool import get_pool

# ------------------------
# AUTH SERVICE FUNCTIONS
# ------------------------

async def get_active_user_contact_by_value(value: str) -> Record | None:
    """
    Получает активный контакт (second_login/email/phone) и связанные данные пользователя.
    Использует функцию accounts.get_active_user_contact_by_value (или аналогичную).
    """
    pool = await get_pool()
    # ⚠️ Важно: в схеме accounts должна существовать такая функция!
    # Если её нет — нужно создать (см. ниже рекомендацию).
    return await pool.fetchrow(
        "SELECT * FROM accounts.get_active_user_contact_by_value($1)",
        value
    )

async def register_user_with_refresh(payload: dict, password: str) -> tuple[Record, str]:
    """
    Создаёт пользователя в accounts и сохраняет refresh токен в auth — в одной транзакции.
    """
    pool = await get_pool()
    password_hash = hash_password(password)
    full_payload = {**payload, "password_hash": password_hash}

    refresh_token, refresh_hash = gen_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    async with pool.acquire() as conn:
        async with conn.transaction():
            # 1. Создаём пользователя + контакты + группы
            user = await conn.fetchrow(
                "SELECT * FROM accounts.create_user_with_relations($1::jsonb)",
                json.dumps(full_payload, ensure_ascii=False, separators=(',', ':'))
            )
            # 2. Сохраняем refresh в auth.refresh_tokens
            await conn.execute(
                "SELECT auth.create_refresh_token($1, $2, $3)",
                str(user["id"]), refresh_hash, expires_at.isoformat()
            )
    return user, refresh_token

async def create_refresh_token(user_id: str, token_hash: str, expires_at: str) -> None:
    """
    Сохраняет refresh token (вызывается после логина/регистрации).
    """
    pool = await get_pool()
    await pool.execute(
        "SELECT auth.create_refresh_token($1, $2, $3)",
        user_id, token_hash, expires_at
    )

async def consume_refresh_token(token_hash: str) -> str:
    """
    Помечает refresh token как использованный и возвращает user_id.
    """
    pool = await get_pool()
    user_id = await pool.fetchval(
        "SELECT auth.consume_refresh_token($1)",
        token_hash
    )
    if not user_id:
        raise ValueError("Invalid refresh token")
    return str(user_id)

async def rotate_refresh_token(user_id: str, new_token_hash: str, expires_at: str) -> None:
    """Сохраняет новый refresh после ротации"""
    pool = await get_pool()
    await pool.execute(
        "SELECT auth.create_refresh_token($1, $2, $3)",
        user_id, new_token_hash, expires_at
    )

async def invalidate_all_refresh_tokens(user_id: str) -> None:
    """Удаляет все refresh-токены пользователя (logout с любого устройства)"""
    pool = await get_pool()
    await pool.execute(
        "SELECT auth.invalidate_all_refresh_tokens($1)",
        user_id
    )

async def blacklist_access_token(redis, jti: str) -> None:
    """Добавляет access_token в чёрный список (уже в logout выше)"""
    ttl = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    await redis.setex(f"blacklist:access:{jti}", ttl, "1")