from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1.routes import router as auth_router
from app.db.pool import close_pool
from app.redis.client import close_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis_client()
    await close_pool()

app = FastAPI(
    title="Auth Service",
    lifespan=lifespan
)

app.include_router(auth_router, prefix="/api/v1/auth")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
