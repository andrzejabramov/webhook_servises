# /auth/

## /app/

### /app/api/v1/deps.py
```commandline
from app.db.pool import get_pool
from app.redis.client import get_redis

async def get_db_pool():
    return await get_pool()

async def get_redis_client():
    return await get_redis()
```

### /app/api/v1/routes.py
```commandline
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
```

### /app/core/config.py
```commandline
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()

class Settings(BaseSettings):
    # PostgreSQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: str = "6379"
    REDIS_DB: str = "0"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = os.getenv("ENV_FILE", ".env")

settings = Settings()
```

### /app/db/functions.py
```commandline
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
```

### /app/db/pool.py
```commandline
from asyncpg import create_pool, Pool
from app.core.config import settings

_pool: Pool | None = None

async def get_pool() -> Pool:
    global _pool
    if _pool is None:
        _pool = await create_pool(dsn=settings.DATABASE_URL, min_size=5, max_size=20)
    return _pool

async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
```

### /app/exceptions/
```commandline

```

### /app/redis/client.py
```commandline

```

### /app/schemas/auth.py
```commandline
from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    login: str = Field(..., example="user123 or user@example.com or +79991234567")
    password: str | None = Field(None, example="secret")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str
```

### /app/servises/auth_service.py
```commandline
from datetime import datetime, timedelta, timezone
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
```

### /app/utils/security.py
```commandline
import hashlib
import secrets
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user_id, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token() -> tuple[str, str]:
    """Возвращает (token, token_hash)"""
    token = secrets.token_urlsafe(64)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def normalize_login(login: str) -> str:
    """Нормализация: email → lower, phone → E.164 (упрощённо)"""
    login = login.strip()
    if "@" in login:
        return login.lower()
    # Простая нормализация телефона: оставить только цифры, добавить +
    digits = "".join(filter(str.isdigit, login))
    if digits.startswith("7"):
        return f"+{digits}"
    if digits.startswith("8"):
        return f"+7{digits[1:]}"
    return login  # fallback
```

### /app/main.py
```commandline
from fastapi import FastAPI
from app.api.v1.routes import router as auth_router
from app.core.config import settings
from contextlib import asynccontextmanager
from app.db.pool import close_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_pool()

app = FastAPI(
    title="Auth Service",
    lifespan=lifespan
)

app.include_router(auth_router, prefix="/api/v1/auth")

```
