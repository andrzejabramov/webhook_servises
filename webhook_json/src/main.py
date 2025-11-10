from contextlib import asynccontextmanager
from fastapi import FastAPI

from webhook_json.src.db.pools import init_pools, close_pools
from webhook_json.src.routers import webhook
from webhook_json.src.routers.accounts import router as accounts_router


@asynccontextmanager
async def lifespan(app):
    await init_pools()
    yield
    await close_pools()


app = FastAPI(lifespan=lifespan)
app.include_router(webhook.router, prefix="/webhook")
app.include_router(accounts_router, prefix="/accounts")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)