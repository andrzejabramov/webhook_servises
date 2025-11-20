from fastapi import HTTPException

class BaseWebhookException(Exception):
    """Базовое исключение уровня приложения. Не наследуется от HTTPException."""
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)