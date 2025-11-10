import json
from typing import Any, Dict, Optional
import asyncpg
from loguru import logger

def maybe_json_dumps(data: Optional[Dict[str, Any]]) -> Optional[str]:
    """Сериализует dict → JSON-строку или возвращает None."""
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False)

def maybe_json_loads(s: Optional[str]) -> Optional[Dict[str, Any]]:
    """Десериализует JSON-строку → dict или возвращает None."""
    if s is None or s == "":
        return None
    if isinstance(s, str):
        return json.loads(s)
    # Если вдруг уже dict (на всякий случай)
    if isinstance(s, dict):
        return s
    raise ValueError(f"Expected str or dict, got {type(s)}")

# def maybe_json_loads(s: Optional[str]) -> Optional[Dict[str, Any]]:
#     if s is None or s == "":
#         return None
#     try:
#         return json.loads(s) if isinstance(s, str) else s
#     except (json.JSONDecodeError, TypeError) as e:
#         # Логируй ошибку, если нужно
#         logger.warning(f"Failed to parse JSON: {s}, error: {e}")
#         return None  # или raise — в зависимости от политики

def normalize_user_row(row: asyncpg.Record) -> dict:
    d = dict(row)
    d["profile"] = maybe_json_loads(d.get("profile"))
    return d