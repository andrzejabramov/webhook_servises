from fastapi import APIRouter, Depends

from src.dependencies.webhook import process_webhook_payload

router = APIRouter(tags=["Webhooks"])

@router.post("",
             summary="Process incoming webhook from payment system",
             description="Validates and stores webhook payload from payment gateway into legacy database (`paydb`).",
             operation_id="process_payment_webhook",
             )
async def get_hook(result = Depends(process_webhook_payload)):
    return result