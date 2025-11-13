from fastapi import APIRouter, Depends, HTTPException, status, Body
from asyncpg import Pool
from uuid import UUID

from src.services.users import UserService
from src.schemas.users import UserCreate, UserUpdate, UserRead
from src.dependencies.db import get_accounts_db_pool_dep


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
    user_id: UUID,
    user_update: UserUpdate = Body(
    examples=[
        {
            "is_active": False,
            "profile": {"key": "value"}
        }
    ]
),
    service: UserService = Depends(lambda pool=Depends(get_accounts_db_pool_dep): UserService(pool))
):
    return await service.update(
        user_id=user_id,
        profile=user_update.profile,      # ← dict или None
        is_active=user_update.is_active   # ← bool или None
    )