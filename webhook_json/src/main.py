from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.db.pools import init_main_db_pool, close_main_db_pool
from src.routers import webhook


@asynccontextmanager
async def lifespan(app):
    await init_main_db_pool()
    yield
    await close_main_db_pool()


app = FastAPI(lifespan=lifespan)
app.include_router(webhook.router, prefix="/webhook")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)