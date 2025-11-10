import asyncio
import sys
from pathlib import Path

# Добавляем src в PYTHONPATH, чтобы импортировать настройки
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src import settings
from loguru import logger

import asyncpg


async def test_db_connection():
    logger.info("Testing database connection...")
    try:
        # Создаём временное соединение (не пул — для простоты)
        conn = await asyncpg.connect(dsn=settings.database_url, timeout=10)
        await conn.execute("SELECT 1")
        await conn.close()
        logger.success("✅ Database connection OK")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    # Минимальная настройка логгера (без файлов — только в консоль)
    logger.remove()
    logger.add(
        sink=sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>"
    )

    success = asyncio.run(test_db_connection())
    sys.exit(0 if success else 1)