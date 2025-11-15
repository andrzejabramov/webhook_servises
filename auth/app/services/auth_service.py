from datetime import datetime, timedelta, timezone

from app.redis.client import get_redis_client
from app.db.functions import get_active_user_contact_by_value, create_refresh_token
from app.utils.security import (
    verify_password,
    create_access_token,
    create_refresh_token as gen_refresh,
    normalize_login,
    hash_token,
)

async def authenticate_user(login: str, password: str | None = None) -> dict | None:
    normalized = normalize_login(login)
    contact = await get_active_user_contact_by_value(normalized)
    if not contact:
        return None

    user_id = str(contact["user_id"])
    password_hash = contact["password_hash"]

    # Если пароль не требуется (например, для phone) — пропускаем проверку
    # Но в текущей логике: пароль нужен для second_login/email
    if password is not None:
        if not password_hash or not verify_password(password, password_hash):
            return None
    # Если password is None → предполагаем passwordless (реализуется отдельно)

    # Генерация токенов
    access_token = create_access_token(user_id)
    refresh_token, refresh_hash = gen_refresh()

    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    await create_refresh_token(user_id, refresh_hash, expires_at.isoformat())

    return {
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

async def revoke_token(jti: str, expire: int):
    redis = await get_redis_client()
    await redis.setex(f"revoked:{jti}", expire, "1")