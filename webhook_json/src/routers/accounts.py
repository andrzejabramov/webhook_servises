from fastapi import APIRouter, Depends, HTTPException, status
from src.services.accounts import UserGroupService
from src.schemas.accounts import UserGroupCreate, UserGroupUpdate, UserGroupRead
from src.dependencies.db import get_db_pool  # ← должен возвращать Pool из app.state.db_pool
from asyncpg import Pool
import uuid

router = APIRouter(prefix="/accounts/user-groups", tags=["Accounts: User Groups"])

async def get_service(pool: Pool = Depends(get_db_pool)) -> UserGroupService:
    return UserGroupService(pool)

@router.post("/", response_model=UserGroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(group: UserGroupCreate, service: UserGroupService = Depends(get_service)):
    return await service.create(group)

@router.get("/{group_id}", response_model=UserGroupRead)
async def read_group(group_id: uuid.UUID, service: UserGroupService = Depends(get_service)):
    group = await service.get_by_id(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="User group not found")
    return group

@router.get("/", response_model=list[UserGroupRead])
async def list_groups(service: UserGroupService = Depends(get_service)):
    return await service.get_all()

@router.patch("/{group_id}", response_model=UserGroupRead)
async def update_group(
    group_id: uuid.UUID,
    group_update: UserGroupUpdate,
    service: UserGroupService = Depends(get_service)
):
    updated = await service.update(group_id, group_update)
    if not updated:
        raise HTTPException(status_code=404, detail="User group not found or update failed")
    return updated