from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.db.pool import get_pool
from app.redis.client import get_redis
from app.utils.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/routers/login")

async def get_db_pool():
    return await get_pool()

async def get_redis_client():
    return await get_redis()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    redis = Depends(get_redis_client)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    jti = payload.get("jti")
    user_id = payload.get("sub")
    if not user_id or not jti:
        raise credentials_exception
    # Проверка чёрного списка
    blacklisted = await redis.get(f"blacklist:access:{jti}")
    if blacklisted:
        raise credentials_exception
    return {"user_id": user_id, "jti": jti}