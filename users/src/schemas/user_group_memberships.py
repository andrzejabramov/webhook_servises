from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


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

