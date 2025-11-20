from fastapi import Depends
from asyncpg import Pool, PostgresError
from loguru import logger

from src.schemas.webhook import WebhookPayload
#from src.db.functions import call_webhook_function
from src.exceptions import DatabaseError, WebhookProcessingError
from src.dependencies.db import get_db_pool
from src.services.db_service import call_webhook_function


async def process_webhook_payload(
    payload: WebhookPayload,
    db_pool: Pool = Depends(get_db_pool)
):
    async with db_pool.acquire() as conn:
        return await call_webhook_function(conn, payload.model_dump())
