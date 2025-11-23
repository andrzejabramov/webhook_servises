from pydantic_settings import BaseSettings
from pydantic import ConfigDict, PostgresDsn, Field, RedisDsn
from pathlib import Path
from typing import Set


class Settings(BaseSettings):
    database_write_url: PostgresDsn
    database_read_url: PostgresDsn
    rabbitmq_url: str
    redis_url: RedisDsn = Field(
        default="redis://localhost:6379/1",
        alias="REDIS_URL",
    )  # используем DB=1
    log_dir: Path = Path("./logs")

    # Настройки загрузки файлов (общие для всех сервисов с bulk-операциями)
    MAX_UPLOAD_FILE_SIZE: int = Field(10 * 1024 * 1024, description="10 MB")
    ALLOWED_UPLOAD_EXTENSIONS: Set[str] = {".csv", ".xlsx", ".xls"}

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",  # рекомендуется явно указать кодировку
        extra="forbid",  # или "ignore", но по умолчанию — "ignore"
    )


settings = Settings()
