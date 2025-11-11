from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

# --- Users_groups ---

class UserGroupBase(BaseModel):
    name: str
    description: Optional[str] = None

class UserGroupCreate(UserGroupBase):
    pass

class UserGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = {
                "is_active": False
            }

class UserGroupRead(UserGroupBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Users ---

class UserBase(BaseModel):
    contact_email: str
    username: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    contact_email: Optional[str] = None
    username: Optional[str] = None
    profile: Optional[str] = None
    is_active: Optional[bool] = None

class UserRead(UserBase):
    id: UUID4
    username: str
    contact_email: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    profile: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}

class UserGroupMembershipBase(BaseModel):
    user_id: UUID
    group_id: int  # int2 в PostgreSQL → int в Python

class UserGroupMembershipCreate(UserGroupMembershipBase):
    pass

class UserGroupMembershipRead(UserGroupMembershipBase):
    is_active: bool
    deactivated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # для Pydantic v2 (ранее orm_mode)

class UserGroupMembershipUpdate(BaseModel):
    is_active: bool

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