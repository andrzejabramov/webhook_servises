from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.db.pools import init_pools, close_pools
from src.routers import webhook


@asynccontextmanager
async def lifespan(app):
    await init_pools()
    yield
    await close_pools()


app = FastAPI(lifespan=lifespan)
app.include_router(webhook.router, prefix="/webhook")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)