# src/exceptions.py
from fastapi import HTTPException

class WebhookProcessingError(HTTPException):
    def __init__(self, detail: str = "Failed to process webhook"):
        super().__init__(status_code=500, detail=detail)

class InvalidWebhookData(HTTPException):
    def __init__(self, detail: str = "Invalid webhook data"):
        super().__init__(status_code=400, detail=detail)

class DatabaseError(HTTPException):
    def __init__(self, detail: str = "Database unavailable"):
        super().__init__(status_code=503, detail=detail)