from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ContactTypeBase(BaseModel):
    name: str

class ContactTypeCreate(ContactTypeBase):
    pass

class ContactTypeRead(ContactTypeBase):
    id: int
    created_at: datetime