from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    login: str = Field(..., example="user123 or user@example.com or +79991234567")
    password: str | None = Field(None, example="secret")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str