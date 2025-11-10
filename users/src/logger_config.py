from loguru import logger
import os
from src.settings import settings

def setup_logger():
    log_dir = settings.log_dir
    os.makedirs(log_dir, exist_ok=True)
    logger.remove()

    # Лог в файл (ежедневная ротация, 6 месяцев, архивация)
    logger.add(
        log_dir / "webhook.log",
        rotation="00:00",
        retention="180 days",
        compression="zip",
        level="INFO",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )

    # Ошибки в stderr (для Docker-логов)
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level="ERROR"
    )

    return logger