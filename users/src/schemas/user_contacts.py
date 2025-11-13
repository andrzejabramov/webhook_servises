from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class UserContactBase(BaseModel):
    user_id: UUID
    contact_type_id: int
    value: str

class UserContactCreate(UserContactBase):
    pass

class UserContactRead(UserContactBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserContactDeactivate(BaseModel):
    is_active: bool = False
