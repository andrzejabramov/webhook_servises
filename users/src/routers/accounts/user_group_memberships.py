from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from asyncpg import Pool
from typing import List

from src.dependencies.db import get_accounts_db_pool_dep
from src.services.accounts import UserGroupMembershipService
from src.schemas.accounts import (
    UserGroupMembershipCreate,
    UserGroupMembershipRead,
    UserGroupMembershipUpdate,
)


router = APIRouter(prefix="/accounts/user-group-memberships", tags=["Accounts: User Group Memberships"])


async def get_membership_service(pool: Pool = Depends(get_accounts_db_pool_dep)) -> UserGroupMembershipService:
    return UserGroupMembershipService(pool)

@router.post("/", response_model=UserGroupMembershipRead, status_code=status.HTTP_201_CREATED)
async def add_user_to_group(
    membership: UserGroupMembershipCreate,
    service: UserGroupMembershipService = Depends(get_membership_service)
):
    return await service.create(membership)


@router.get("/", response_model=List[UserGroupMembershipRead])
async def list_user_groups(
    user_id: UUID,
    only_active: bool = Query(True, description="Return only active memberships"),
    service: UserGroupMembershipService = Depends(get_membership_service)
):
    return await service.get_user_groups(user_id, only_active=only_active)


@router.get("/{user_id}/{group_id}", response_model=UserGroupMembershipRead)
async def get_membership(
    user_id: UUID,
    group_id: int,
    service: UserGroupMembershipService = Depends(get_membership_service)
):
    membership = await service.get(user_id, group_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    return membership


@router.patch("/{user_id}/{group_id}/deactivate", response_model=UserGroupMembershipRead)
async def deactivate_membership(
    user_id: UUID,
    group_id: int,
    service: UserGroupMembershipService = Depends(get_membership_service)
):
    return await service.deactivate(user_id, group_id)


@router.patch("/{user_id}/{group_id}/reactivate", response_model=UserGroupMembershipRead)
async def reactivate_membership(
    user_id: UUID,
    group_id: int,
    service: UserGroupMembershipService = Depends(get_membership_service)
):
    return await service.reactivate(user_id, group_id)

