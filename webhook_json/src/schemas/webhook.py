# src/webhook.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any, Dict
from datetime import datetime
from decimal import Decimal

class WebhookPayload(BaseModel):
    model_config = ConfigDict(extra="allow")  # разрешить любые дополнительные поля

    Id: str
    MID: str
    Amount: str
    ReaderId: str
    CreatedAt: str
    Inputtype: int
    ClientName: str
    Description: str