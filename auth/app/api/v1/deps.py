from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from jwt.exceptions import InvalidTokenError as JWTInvalidTokenError
from app.core.config import settings
from app.db.pool import get_pool
from app.redis.client import get_redis_client
from app.utils.security import decode_access_token
from app.exceptions.auth import (
    InvalidTokenError,
    TokenRevokedError,
)


security = HTTPBearer()

async def get_db_pool():
    return await get_pool()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis = Depends(get_redis_client)
)-> dict:
    """
    Извлекает и валидирует JWT access-токен.
    Возвращает словарь: {"user_id": str, "jti": str}
    """
    token = credentials.credentials
        # credentials_exception = HTTPException(
    try:
        # Декодируем токен
        # status_code=status.HTTP_401_UNAUTHORIZED,
        # detail="Could not validate credentials",
        # headers={"WWW-Authenticate": "Bearer"},
        # )
        #payload = decode_access_token(token)
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id: str | None = payload.get("sub")
        jti: str | None = payload.get("jti")
        token_type: str | None = payload.get("type")

        if not user_id or not jti:
            raise InvalidTokenError("Missing required claims: sub or jti")

        if token_type != "access":
            raise InvalidTokenError("Invalid token type: expected 'access'")

        # Проверка чёрного списка Redis
        if await redis.exists(f"blacklist:access:{jti}"):
            raise TokenRevokedError()

        return {"user_id": user_id, "jti": jti}


    except JWTInvalidTokenError:
        raise InvalidTokenError()

