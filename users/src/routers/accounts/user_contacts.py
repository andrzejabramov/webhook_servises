from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from asyncpg import Pool
from typing import List

from src.dependencies.db import get_read_db_pool, get_write_db_pool
from src.services.user_contacts import UserContactService
from src.schemas.user_contacts import UserContactCreate, UserContactRead


router = APIRouter(prefix="/accounts/contacts", tags=["Accounts: User Contacts"])


async def get_contact_service(pool: Pool = Depends(get_read_db_pool)) -> UserContactService:
    return UserContactService(pool)

@router.post("/", response_model=UserContactRead, status_code=status.HTTP_201_CREATED)
async def create_user_contact(
    contact: UserContactCreate,
    service: UserContactService = Depends(get_write_db_pool)
):
    return await service.create(contact)


@router.get("/{contact_id}", response_model=UserContactRead)
async def get_contact(
    contact_id: UUID,
    service: UserContactService = Depends(get_read_db_pool)
):
    contact = await service.get_by_id(contact_id)
    if not contact:
        raise ContactNotFound(contact_id=str(contact_id))
    return contact


@router.get("/user/{user_id}", response_model=List[UserContactRead])
async def list_user_contacts(
    user_id: UUID,
    only_active: bool = Query(True, description="Return only active contacts"),
    service: UserContactService = Depends(get_read_db_pool)
):
    return await service.get_by_user_id(user_id, only_active=only_active)


@router.patch("/{contact_id}/deactivate", response_model=UserContactRead)
async def deactivate_contact(
    contact_id: UUID,
    service: UserContactService = Depends(get_write_db_pool)
):
    return await service.deactivate(contact_id)


@router.patch("/{contact_id}/reactivate", response_model=UserContactRead)
async def reactivate_contact(
    contact_id: UUID,
    service: UserContactService = Depends(get_write_db_pool)
):
    return await service.reactivate(contact_id)
