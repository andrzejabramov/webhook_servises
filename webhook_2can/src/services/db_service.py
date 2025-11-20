from asyncpg import Connection, PostgresError
from loguru import logger

from src.exceptions import InvalidWebhookData

async def call_webhook_function(conn: Connection, payload: dict) -> dict:
    try:
        logger.debug(f"Calling DB function with keys: {list(payload.keys())}")
        result = await conn.fetchval("SELECT to_can.process_webhook($1)", payload)

        if isinstance(result, dict) and result.get("error"):
            logger.warning(f"DB rejected webhook: {result['error']}")
            raise InvalidWebhookData(detail=result["error"])

        logger.info("Webhook processed successfully")
        return result or {"status": "success"}

    except PostgresError as err:
        logger.error(f"PostgreSQL error: {e}")
        raise DatabaseError(detail="Database operation failed")
    except Exception as e:
        logger.exception("Unexpected error in DB function")
        raise WebhookProcessingError(detail="Internal error during DB call")


    except Exception:
        logger.exception("Exception in DB function call")
        raise