from pydantic import BaseModel, UUID4, Field, field_validator
from typing import Optional, Dict, Any, Literal, List
from datetime import datetime
from uuid import UUID
import phonenumbers


class UserBase(BaseModel):
    is_active: Optional[bool] = None
    profile: Optional[Dict[str, Any]] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    profile: Optional[Dict[str, Any]] = None

class UserRead(UserBase):
    id: UUID
    username: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    profile: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import phonenumbers

class BulkUserItem(BaseModel):
    phone: str
    external_id: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone")
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            raise ValueError(f"Invalid phone format: {e}")

class BulkCreateRequest(BaseModel):
    interface: str  # "driver" или "courier" — для назначения роли
    users: List[BulkUserItem] = Field(..., min_length=1, max_length=1000)

class BulkCreateResult(BaseModel):
    created: int
    skipped: int
    errors: List[dict]