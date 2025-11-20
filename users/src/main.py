from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from src.middleware.request_id import RequestIDMiddleware
from src.middleware.logging import LoggingMiddleware
from src.db.pools import init_pools, close_pools
from src.routers.accounts import router as accounts_router
from src.settings import settings
from src.logger_config import setup_logger
from src.core.handlers import register_exception_handlers


logger = setup_logger()
logger.info("✅ Logger is configured and working")

@asynccontextmanager
async def lifespan(app):
    await init_pools()
    yield
    await close_pools()


app = FastAPI(lifespan=lifespan)

# Регистрируем обработчики исключений ДО подключения роутеров (рекомендуется, но не критично)
register_exception_handlers(app)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)  # при возврате списков пользователей

app.include_router(accounts_router, prefix="/accounts")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)