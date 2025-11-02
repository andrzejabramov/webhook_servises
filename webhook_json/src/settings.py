from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path


class Settings(BaseSettings):
    database_url: str
    rabbitmq_url: str
    log_dir: Path = Path("./logs")

    # # PostgreSQL
    # postgres_db: str
    # postgres_user: str
    # postgres_password: str

    # # RabbitMQ
    # rabbitmq_default_user: str
    # rabbitmq_default_pass: str

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",  # рекомендуется явно указать кодировку
        extra="forbid",  # или "ignore", но по умолчанию — "ignore"
    )


settings = Settings()
