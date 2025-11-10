from asyncpg import Connection
from loguru import logger

from webhook_json.src.exceptions.exceptions import InvalidWebhookData

async def call_webhook_function(conn: Connection, payload: dict) -> dict:
    try:
        logger.debug(f"Calling DB function with keys: {list(payload.keys())}")
        result = await conn.fetchval("SELECT two_can.process_webhook($1)", payload)

        if isinstance(result, dict) and result.get("error"):
            logger.warning(f"DB rejected webhook: {result['error']}")
            raise InvalidWebhookData(detail=result["error"])

        logger.info("Webhook processed successfully")
        return result

    except Exception:
        logger.exception("Exception in DB function call")
        raise