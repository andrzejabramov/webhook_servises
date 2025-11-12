from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest
from app.services.auth_service import authenticate_user
from app.db.functions import consume_refresh_token
from app.utils.security import create_access_token, hash_token

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    if not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required for now"
        )
    user = await authenticate_user(request.login, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return TokenResponse(
        access_token=user["access_token"],
        refresh_token=user["refresh_token"]
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest):
    token_hash = hash_token(request.refresh_token)
    try:
        user_id = await consume_refresh_token(token_hash)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    new_access = create_access_token(user_id)
    # Новый refresh не выдаём (одноразовый)
    # Или выдаём — по вашему выбору
    return TokenResponse(
        access_token=new_access,
        refresh_token=""  # или сгенерировать новый
    )