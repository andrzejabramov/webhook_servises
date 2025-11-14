from pydantic import BaseModel, ConfigDict

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