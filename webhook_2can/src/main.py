from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.middleware.request_id import RequestIDMiddleware
from src.middleware.logging import LoggingMiddleware
from src.db.pools import init_pools, close_pools
from src.routers import webhook
from src.exceptions import (
    BaseWebhookException,
    InvalidWebhookData,
    WebhookProcessingError,
    DatabaseError,
)


@asynccontextmanager
async def lifespan(app):
    await init_pools()
    yield
    await close_pools()


app = FastAPI(lifespan=lifespan)

# --- Exception handlers ---
@app.exception_handler(InvalidWebhookData)
async def invalid_webhook_data_handler(request, exc: InvalidWebhookData):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.detail}
    )

@app.exception_handler(DatabaseError)
async def database_error_handler(request, exc: DatabaseError):
    return JSONResponse(
        status_code=503,
        content={"detail": exc.detail}
    )

@app.exception_handler(WebhookProcessingError)
async def webhook_processing_error_handler(request, exc: WebhookProcessingError):
    return JSONResponse(
        status_code=500,
        content={"detail": exc.detail}
    )

# Общий fallback для BaseWebhookException
@app.exception_handler(BaseWebhookException)
async def base_webhook_exception_handler(request, exc: BaseWebhookException):
    return JSONResponse(
        status_code=500,
        content={"detail": exc.detail}
    )

app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← ограничь в продакшене!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router, prefix="/webhook")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)