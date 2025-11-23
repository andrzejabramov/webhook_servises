from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Body,
    UploadFile,
    File,
    Query,
)
from loguru import logger
from asyncpg import Pool
from uuid import UUID

from src.services.users import (
    UserService,
    bulk_create_users_from_file,
    UserDetailRead,
)
from src.db.redis import redis
from src.utils.json_utils import maybe_json_loads, maybe_json_dumps
from src.dependencies.db import get_read_db_pool, get_write_db_pool
from src.dependencies.upload import validate_upload_file
from src.schemas.common import PaginatedResponse
from src.exceptions.exceptions import ValidationError, UserNotFound
from src.schemas.users import (
    UserCreate,
    UserUpdate,
    UserRead,
    BulkCreateRequest,
    BulkCreateResult,
    UploadResult,
)


router = APIRouter(tags=["Accounts: Users"])

async def get_user_service(pool: Pool = Depends(get_read_db_pool)) -> UserService:
    return UserService(pool)

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, service: UserService = Depends(get_write_db_pool)):
    return await service.create(user)

@router.get("/", response_model=PaginatedResponse[UserRead])
async def get_user_list(
        page: int = Query(1, ge=1, description="Номер страницы"),
        size: int = Query(50, ge=1, le=100, description="Размер страницы (макс. 100)"),
        service: UserService = Depends(get_read_db_pool)
):
    return await service.get_paginated(page=page, size=size)

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
    service: UserService = Depends(lambda pool=Depends(get_write_db_pool): UserService(pool))
):
    return await service.update(
        user_id=user_id,
        profile=user_update.profile,      # ← dict или None
        is_active=user_update.is_active,   # ← bool или None
    )

@router.post("/bulk", response_model=BulkCreateResult)
async def bulk_create_users(
        request: BulkCreateRequest,
        service: UserService = Depends(get_write_db_pool),
):
    try:
        return await service.bulk_create_users(interface=request.interface, users=request.users)
    except ValueError as e:
        raise ValidationError("bulk_create", "users", str(e))

@router.post("/bulk/upload", response_model=UploadResult)
async def bulk_create_users_upload(file: UploadFile = Depends(validate_upload_file)):
    """
    Загружает файл с колонками: phone, user_groups.
    Пример user_groups: "client,driver" (через запятую).
    """
    return await process_user_groups_bulk_upload(file)

@router.get("/by-identifier", response_model=UserDetailRead)
async def get_user_by_identifier(
    identifier: str = Query(..., min_length=1, max_length=255, description="UUID, email, phone (+7...), or second_login"),
    pool: Pool = Depends(get_read_db_pool)
):
    cache_key = f"user_by_id:{identifier}"
    cached = await redis.get(cache_key)
    if cached:
        logger.debug(f"Cache hit for identifier: {identifier}")
        data = json.loads(cached)
        data["profile"] = maybe_json_loads(data.get("profile"))
        return UserDetailRead(**data)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM accounts.get_user_by_identifier_v1($1)",
            identifier
        )
        if not row:
            raise UserNotFound(user_id=identifier)

    # Формируем ответ
    user_dict = {
        "id": row["id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "is_active": row["is_active"],
        "profile": row["profile"],
        "groups": row["groups"],
        "contacts": row["contacts"],
    }

    # Подготовка к кэшированию
    cache_data = user_dict.copy()
    cache_data["profile"] = maybe_json_dumps(cache_data["profile"])

    # Кэшируем на 10 минут
    await redis.setex(cache_key, 600, json.dumps(cache_data, default=str))
    logger.info(f"Cached user by identifier: {identifier}")

    @router.get("/by-identifier", response_model=UserDetailRead)
    async def get_user_by_identifier(
            identifier: str = Query(..., min_length=1, max_length=255,
                                    description="UUID, email, phone (+7...), or second_login"),
            pool: Pool = Depends(get_read_db_pool)
    ):
        cache_key = f"user_by_id:{identifier}"
        cached = await redis.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for identifier: {identifier}")
            data = json.loads(cached)
            data["profile"] = maybe_json_loads(data.get("profile"))
            return UserDetailRead(**data)

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM accounts.get_user_by_identifier_v1($1)",
                identifier
            )
            if not row:
                raise UserNotFound(user_id=identifier)

        # Формируем ответ
        user_dict = {
            "id": row["id"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "is_active": row["is_active"],
            "profile": row["profile"],
            "groups": row["groups"],
            "contacts": row["contacts"],
        }

        # Подготовка к кэшированию
        cache_data = user_dict.copy()
        cache_data["profile"] = maybe_json_dumps(cache_data["profile"])

        # Кэшируем на 10 минут
        await redis.setex(cache_key, 600, json.dumps(cache_data, default=str))
        logger.info(f"Cached user by identifier: {identifier}")

        @router.get("/by-identifier", response_model=UserDetailRead)
        async def get_user_by_identifier(
                identifier: str = Query(..., min_length=1, max_length=255,
                                        description="UUID, email, phone (+7...), or second_login"),
                pool: Pool = Depends(get_read_db_pool)
        ):
            return await get_user_by_identifier_cached(identifier, pool)