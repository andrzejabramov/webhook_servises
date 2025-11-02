from fastapi import APIRouter, Depends

from src.dependencies.webhook import process_webhook_payload

router = APIRouter()

@router.post("", tags=["webhook"])
async def get_hook(result = Depends(process_webhook_payload)):
    return result