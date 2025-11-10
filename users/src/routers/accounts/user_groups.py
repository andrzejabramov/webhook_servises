from fastapi import APIRouter, Depends, HTTPException, status, Body
from asyncpg import Pool

from users.src.services.accounts import UserGroupService
from users.src.schemas.accounts import UserGroupCreate, UserGroupUpdate, UserGroupRead
from users.src.dependencies.db import get_accounts_db_pool_dep  # ← должен возвращать Pool из app.state.db_pool

import uuid

router = APIRouter(tags=["Accounts / User Groups"])

async def get_service(pool: Pool = Depends(get_accounts_db_pool_dep)) -> UserGroupService:
    return UserGroupService(pool)

@router.post("/",
             response_model=UserGroupRead,
             status_code=status.HTTP_201_CREATED,
             operation_id="create_user_group",
             description="Creates a new group with unique name. The group is active by default.",
             summary="Create a new user group",
             )
async def create_group(group: UserGroupCreate, service: UserGroupService = Depends(get_service)):
    return await service.create(group)

@router.get("/",
            response_model=list[UserGroupRead],
            summary="List all user groups",
            )
async def list_groups(service: UserGroupService = Depends(get_service)):
    return await service.get_all()

@router.patch("/{group_id}",
              response_model=UserGroupRead,
              summary="Update user group fields",
              description="Partial update. Send only fields you want to change. "
              "Use GET / to find the group and copy its data if needed.",
)
async def update_group(
    group_id: int,
    service: UserGroupService = Depends(get_service),
    group_update: UserGroupUpdate = Body(
        examples=[
            {
                "is_active": False
            },
            {
                "name": "Super Admins",
                "description": "Full system access"
            }
        ]
    )
):
    updated = await service.update(group_id, group_update)
    if not updated:
        raise HTTPException(status_code=404, detail="User group not found or update failed")
    return updated