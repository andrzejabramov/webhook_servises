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

class UserContactBase(BaseModel):
    user_id: UUID            # ← ссылка на users.id (uuid)
    contact_type_id: int     # ← ссылка на contact_types.id (int!)
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

class ContactTypeBase(BaseModel):
    name: str

class ContactTypeCreate(ContactTypeBase):
    pass

class ContactTypeRead(ContactTypeBase):
    id: int
    created_at: datetime