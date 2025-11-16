from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from jwt.exceptions import InvalidTokenError
from app.core.config import settings
from app.db.pool import get_pool
from app.redis.client import get_redis_client
from app.utils.security import decode_access_token


security = HTTPBearer()

async def get_db_pool():
    return await get_pool()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    #token: str = Depends(oauth2_scheme),
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
        # if payload is None:
        #     raise credentials_exception
        # jti = payload.get("jti")
        # user_id = payload.get("sub")

        user_id: str | None = payload.get("sub")
        jti: str | None = payload.get("jti")
        token_type: str | None = payload.get("type")

        if not user_id or not jti:
            raise InvalidTokenError("Missing required claims: sub or jti")

        if token_type != "access":
            raise InvalidTokenError("Invalid token type: expected 'access'")

        # Проверка чёрного списка Redis
        if await redis.exists(f"blacklist:access:{jti}"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        # blacklisted = await redis.get(f"blacklist:access:{jti}")
        # if blacklisted:
        #     raise credentials_exception
        return {"user_id": user_id, "jti": jti}

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

