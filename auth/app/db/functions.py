from asyncpg import Record
from app.db.pool import get_pool

async def get_active_user_contact_by_value(value: str) -> Record | None:
    """Получает активный контакт (email/phone/second_login) и user_id + password_hash"""
    pool = await get_pool()
    query = """
        SELECT
            uc.user_id,
            u.password_hash
        FROM accounts.user_contacts uc
        JOIN accounts.contact_types ct ON uc.contact_type_id = ct.id
        JOIN accounts.users u ON uc.user_id = u.id
        WHERE uc.value = $1
          AND uc.is_active = TRUE
          AND ct.name = ANY(ARRAY['second_login', 'email', 'phone'])
          AND u.status = TRUE
    """
    return await pool.fetchrow(query, value)

async def create_refresh_token(user_id: str, token_hash: str, expires_at: str) -> None:
    pool = await get_pool()
    await pool.execute(
        "SELECT auth.create_refresh_token($1, $2, $3)",
        user_id, token_hash, expires_at
    )

async def consume_refresh_token(token_hash: str) -> str:
    pool = await get_pool()
    user_id = await pool.fetchval(
        "SELECT auth.consume_refresh_token($1)",
        token_hash
    )
    if not user_id:
        raise ValueError("Invalid refresh token")
    return str(user_id)