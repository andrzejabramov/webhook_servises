from asyncpg import Connection
from typing import Any, Dict
import json

async def call_webhook_function(conn: Connection, payload: Dict[str, Any]) -> Any:
    # Пример: вызов функции в схеме to_can
    json_str = json.dumps(payload, ensure_ascii=False)
    result = await conn.fetchval(
        "SELECT to_can.f_syspay($1::json)",
        json_str
    )
    return result
