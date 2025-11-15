from pydantic import BaseModel, Field
from typing import Optional, List, Any


class LoginRequest(BaseModel):
    login: str = Field(..., example="user123 or user@example.com or +79991234567")
    password: str | None = Field(None, example="secret")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class RegisterRequest(BaseModel):
    second_login: str = Field(..., min_length=3, max_length=64)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    profile: Optional[dict[str, Any]] = None
    password: str = Field(..., min_length=8)
    group_names: List[str] = Field(
        ...,
        min_items=1,
        example=["customer"]
    )

class LogoutRequest(BaseModel):
    pass