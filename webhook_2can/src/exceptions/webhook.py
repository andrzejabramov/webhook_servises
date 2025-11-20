from .base import BaseWebhookException

class WebhookProcessingError(BaseWebhookException):
    pass

class InvalidWebhookData(BaseWebhookException):
    pass

class DatabaseError(BaseWebhookException):
    pass