from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Body,
    UploadFile,
    File,
)
from asyncpg import Pool
from uuid import UUID

from src.services.users import UserService, bulk_create_users_from_file
from src.dependencies.db import get_accounts_db_pool_dep
from src.dependencies.upload import validate_upload_file
from src.schemas.users import (
    UserCreate,
    UserUpdate,
    UserRead,
    BulkCreateRequest,
    BulkCreateResult,
    UploadResult,
)


router = APIRouter(tags=["Accounts: Users"])

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
        is_active=user_update.is_active,   # ← bool или None
    )

@router.post("/bulk", response_model=BulkCreateResult)
async def bulk_create_users(
        request: BulkCreateRequest,
        service: UserService = Depends(get_user_service),
):
    try:
        return await service.bulk_create_users(interface=request.interface, users=request.users)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bulk/upload", response_model=UploadResult)
async def bulk_create_users_upload(file: UploadFile = Depends(validate_upload_file)):
    """
    Загружает файл с колонками: phone, user_groups.
    Пример user_groups: "client,driver" (через запятую).
    """
    return await process_user_groups_bulk_upload(file)
