from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta, timezone

from app.api.v1.deps import get_redis_client, get_current_user
from app.core.config import settings
from app.services.auth_service import authenticate_user
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    RegisterRequest,
)
from app.db.functions import (
    consume_refresh_token,
    register_user_with_refresh,
    rotate_refresh_token,
    invalidate_all_refresh_tokens,
)
from app.utils.security import (
    create_access_token,
    hash_token,
    create_refresh_token,
)
from app.exceptions.auth import (
    PasswordRequiredError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    InvalidGroupError,
    RegistrationFailedError,
)


router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    if not request.password:
        raise PasswordRequiredError()
    user = await authenticate_user(request.login, request.password)
    if not user:
        raise InvalidCredentialsError()
    return TokenResponse(
        access_token=user["access_token"],
        refresh_token=user["refresh_token"]
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest):
    token_hash = hash_token(request.refresh_token)
    try:
        user_id = await consume_refresh_token(token_hash)  # возвращает user_id и удаляет refresh
    except ValueError:
        raise InvalidTokenError("Invalid or expired refresh token")
    # Генерируем новые токены
    new_access = create_access_token(user_id)
    new_refresh, new_refresh_hash = create_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    # Сохраняем новый refresh
    await rotate_refresh_token(user_id, new_refresh_hash, expires_at.isoformat())
    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh
    )

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    try:
        # Подготавливаем payload без пароля (он хешируется внутри)
        payload = {
            "second_login": request.second_login,
            "phone": request.phone,
            "email": request.email,
            "profile": request.profile or {},
            "group_names": request.group_names,
        }
        user, refresh_token = await register_user_with_refresh(payload, request.password)
        access_token = create_access_token(str(user["id"]))
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        # Ловим уникальность, отсутствие групп и т.д.
        err_msg = str(e)
        if "already exists" in err_msg:
            raise UserAlreadyExistsError(detail=err_msg)
        elif "not found" in err_msg:
            raise InvalidGroupError(detail=err_msg)
        else:
            raise RegistrationFailedError(detail=err_msg)
    except Exception as e:
        err_msg = str(e)
        if "already exists" in err_msg:
            raise UserAlreadyExistsError(detail=err_msg)
        elif "not found" in err_msg:
            raise InvalidGroupError(detail=err_msg)
        raise RegistrationFailedError()

@router.post("/logout")
async def logout(
    redis=Depends(get_redis_client),
    current_user: dict = Depends(get_current_user)  # ← нужно реализовать!
):
    access_jti = current_user["jti"]  # ← можно извлечь из JWT
    user_id = current_user["user_id"]

    # 1. Черный список access
    ttl = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    await redis.setex(f"blacklist:access:{access_jti}", ttl, "1")

    # 2. Инвалидировать все refresh-токены пользователя
    await invalidate_all_refresh_tokens(user_id)

    return {"detail": "Successfully logged out"}