from fastapi import APIRouter, Depends, HTTPException, status, Body
from asyncpg import Pool

from webhook_json.src.services.accounts import UserService
from webhook_json.src.schemas.accounts import UserCreate, UserUpdate, UserRead
from webhook_json.src.dependencies.db import get_accounts_db_pool_dep
f

router = APIRouter(prefix="/accounts/users", tags=["Accounts: Users"])

async def get_user_service(pool: Pool = Depends(get_accounts_db_pool_dep)) -> UserService:
    return UserService(pool)

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    return await service.create(user)

@router.get("/", response_model=list[UserRead])
async def list_users(service: UserService = Depends(get_user_service)):
    return await service.get_all()

@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: UserUpdate = Body(
    examples=[
        {"summary": "Deactivate user", "value": {"is_active": False}},
        {"summary": "Update name", "value": {"full_name": "John Doe"}}
    ]
),
    #user_update: UserUpdate,
    service: UserService = Depends(get_user_service)
):
    updated = await service.update(user_id, user_update)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated