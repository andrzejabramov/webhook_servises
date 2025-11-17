from typing import Optional, Dict, Any

class AppException(Exception):
    """Базовый класс для всех управляемых исключений в сервисе."""
    def __init__(
        self,
        message: str,
        status_code: int,
        error_code: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


# === Общие ошибки (можно использовать в любом сервисе) ===

class ValidationError(AppException):
    def __init__(self, field: str, value: str, reason: str = "Invalid value"):
        super().__init__(
            message=reason,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details={"field": field, "value": value},
        )

class NotFoundError(AppException):
    def __init__(self, entity: str, entity_id: str):
        super().__init__(
            message=f"{entity} not found",
            status_code=404,
            error_code="NOT_FOUND",
            details={"entity": entity, "id": entity_id},
        )

class DatabaseError(AppException):
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            message=detail,
            status_code=503,
            error_code="DATABASE_ERROR",
            details={},
        )


# === Специфичные ошибки users ===

class UserNotFound(NotFoundError):
    def __init__(self, user_id: str):
        super().__init__("User", user_id)

class InvalidSecondLogin(AppException):
    def __init__(self, second_login: str):
        super().__init__(
            message="second_login must be unique and valid",
            status_code=400,
            error_code="INVALID_SECOND_LOGIN",
            details={"second_login": second_login},
        )

class GroupNotFound(NotFoundError):
    def __init__(self, group_id: str):
        super().__init__("Group", group_id)

class ContactTypeConflict(AppException):
    def __init__(self, contact_type: str, user_id: str):
        super().__init__(
            message="Only one active contact per type allowed",
            status_code=409,
            error_code="CONTACT_TYPE_CONFLICT",
            details={"contact_type": contact_type, "user_id": user_id},
        )
