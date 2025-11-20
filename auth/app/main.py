from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.request_id import RequestIDMiddleware
from app.middleware.logging import LoggingMiddleware
from app.api.v1.routes import router as auth_router
from app.db.pool import close_pool
from app.redis.client import close_redis_client
from app.exceptions.auth import (
    InvalidCredentialsError,
    TokenExpiredError,
    TokenRevokedError,
    InvalidTokenError,
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidGroupError,
    PasswordRequiredError,
    RegistrationFailedError,
)
from app.exceptions.base import BaseAPIException


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis_client()
    await close_pool()

app = FastAPI(
    title="Auth Service",
    lifespan=lifespan
)

# ← Добавить обработчики
@app.exception_handler(BaseAPIException)
async def base_api_exception_handler(request, exc: BaseAPIException):
    return exc  # BaseAPIException наследуется от HTTPException → FastAPI сам сериализует

app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router, prefix="/api/v1/auth")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
