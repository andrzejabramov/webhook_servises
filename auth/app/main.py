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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
