from fastapi import status
from .base import BaseAPIException

class InvalidCredentialsError(BaseAPIException):
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class TokenExpiredError(BaseAPIException):
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class TokenRevokedError(BaseAPIException):
    def __init__(self, detail: str = "Token has been revoked"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class InvalidTokenError(BaseAPIException):
    def __init__(self, detail: str = "Invalid or malformed token"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class UserNotFoundError(BaseAPIException):
    def __init__(self, detail: str = "User not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class UserAlreadyExistsError(BaseAPIException):
    def __init__(self, detail: str = "User with this identifier already exists"):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)

class InvalidGroupError(BaseAPIException):
    def __init__(self, detail: str = "One or more groups do not exist"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)

class PasswordRequiredError(BaseAPIException):
    def __init__(self, detail: str = "Password is required"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)

class RegistrationFailedError(BaseAPIException):
    def __init__(self, detail: str = "Registration failed due to internal error"):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)