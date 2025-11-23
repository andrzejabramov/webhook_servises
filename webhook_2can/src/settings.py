from pydantic_settings import BaseSettings
from pydantic import ConfigDict, PostgresDsn
from pathlib import Path


class Settings(BaseSettings):
    database_write_url: PostgresDsn
    database_read_url: PostgresDsn
    rabbitmq_url: str
    log_dir: Path = Path("./logs")

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",  # рекомендуется явно указать кодировку
        extra="forbid",  # или "ignore", но по умолчанию — "ignore"
    )


settings = Settings()
