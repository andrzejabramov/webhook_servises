from fastapi import Depends
from asyncpg import Pool, PostgresError
from loguru import logger

from webhook_json.src.schemas.webhook import WebhookPayload
from webhook_json.src.db.functions import call_webhook_function
from webhook_json.src.exceptions.exceptions import DatabaseError, WebhookProcessingError
from webhook_json.src.dependencies.db import get_db_pool

async def process_webhook_payload(
    payload: WebhookPayload,
    db_pool: Pool = Depends(get_db_pool)
):
    try:
        async with db_pool.acquire() as conn:
            result = await call_webhook_function(conn, payload.model_dump())
        return result
    except PostgresError as e:
        logger.error(f"PostgreSQL error: {e}")
        raise DatabaseError(detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise WebhookProcessingError(detail="Internal processing error")