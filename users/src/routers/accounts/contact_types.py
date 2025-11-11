# src/routers/accounts/contact_types.py
from fastapi import APIRouter, Depends, status
from asyncpg import Pool
from src.dependencies.db import get_accounts_db_pool_dep
from src.services.accounts import ContactTypeService
from src.schemas.accounts import ContactTypeCreate, ContactTypeRead

router = APIRouter(prefix="/accounts/contact-types", tags=["Accounts: Contact Types"])

def get_contact_type_service(pool: Pool = Depends(get_accounts_db_pool_dep)) -> ContactTypeService:
    return ContactTypeService(pool)

@router.post("/", response_model=ContactTypeRead, status_code=status.HTTP_201_CREATED)
async def create_contact_type(
    data: ContactTypeCreate,
    service: ContactTypeService = Depends(get_contact_type_service)
):
    return await service.create(data)

@router.get("/", response_model=list[ContactTypeRead])
async def list_contact_types(
    service: ContactTypeService = Depends(get_contact_type_service)
):
    return await service.list_all()