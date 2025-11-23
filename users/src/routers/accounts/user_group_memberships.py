from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from asyncpg import Pool
from typing import List

from src.dependencies.db import get_read_db_pool, get_write_db_pool
from src.services.user_group_memberships import UserGroupMembershipService
from src.exceptions.exceptions import NotFoundError
from src.schemas.user_group_memberships import (
    UserGroupMembershipCreate,
    UserGroupMembershipRead,
    UserGroupMembershipUpdate,
)


router = APIRouter(prefix="/accounts/user-group-memberships", tags=["Accounts: User Group Memberships"])


async def get_membership_service(pool: Pool = Depends(get_read_db_pool)) -> UserGroupMembershipService:
    return UserGroupMembershipService(pool)

@router.post("/", response_model=UserGroupMembershipRead, status_code=status.HTTP_201_CREATED)
async def add_user_to_group(
    membership: UserGroupMembershipCreate,
    service: UserGroupMembershipService = Depends(get_write_db_pool)
):
    return await service.create(membership)


@router.get("/", response_model=List[UserGroupMembershipRead])
async def list_user_groups(
    user_id: UUID,
    only_active: bool = Query(True, description="Return only active memberships"),
    service: UserGroupMembershipService = Depends(get_read_db_pool)
):
    return await service.get_user_groups(user_id, only_active=only_active)


@router.get("/{user_id}/{group_id}", response_model=UserGroupMembershipRead)
async def get_membership(
    user_id: UUID,
    group_id: int,
    service: UserGroupMembershipService = Depends(get_read_db_pool)
):
    membership = await service.get(user_id, group_id)
    if not membership:
        raise NotFoundError("Membership", f"{user_id}/{group_id}")
    return membership


@router.patch("/{user_id}/{group_id}/deactivate", response_model=UserGroupMembershipRead)
async def deactivate_membership(
    user_id: UUID,
    group_id: int,
    service: UserGroupMembershipService = Depends(get_write_db_pool)
):
    return await service.deactivate(user_id, group_id)


@router.patch("/{user_id}/{group_id}/reactivate", response_model=UserGroupMembershipRead)
async def reactivate_membership(
    user_id: UUID,
    group_id: int,
    service: UserGroupMembershipService = Depends(get_write_db_pool)
):
    return await service.reactivate(user_id, group_id)

