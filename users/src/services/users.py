from fastapi import Depends, UploadFile
from asyncpg import Pool
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from src.utils.json_utils import maybe_json_loads
from src.schemas.common import PaginatedResponse
from src.dependencies.db import get_accounts_db_pool_dep
from src.utils.json_utils import (
    normalize_user_row,
    maybe_json_dumps,
    maybe_json_loads,
)
from src.schemas.users import (
    UserCreate,
    UserUpdate,
    UserRead,
    BulkUserItem,
    UserBulkCreateRow,
    UploadResult,
    UserReadExtended,
)


logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def create(self, user: UserCreate) -> UserRead:
        query = 'SELECT * FROM accounts.create_user($1::text, $2::jsonb)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                maybe_json_dumps(user.profile),
            )
        row_dict = dict(row)
        row_dict["profile"] = maybe_json_loads(row_dict.get("profile"))
        return UserRead(**normalize_user_row(row_dict))

    async def get_by_id(self, user_id: int) -> Optional[UserRead]:
        query = 'SELECT * FROM accounts.get_user($1)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id)
        return UserRead(**normalize_user_row(row)) if row else None

    async def get_all(self) -> List[UserRead]:
        query = 'SELECT * FROM accounts.list_users()'
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
        return [UserRead(**normalize_user_row(row)) for row in rows]

    async def update(
            self,
            user_id: UUID,
            is_active: Optional[bool] = None,
            profile: Optional[Dict[str, Any]] = None,
    ) -> UserRead:
        profile_json: Optional[str] = maybe_json_dumps(profile)
        query = 'SELECT * FROM accounts.update_user_profile($1, $2, $3)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                user_id,
                is_active,
                profile_json,
            )
        return UserRead(**normalize_user_row(row)) if row else None

    async def bulk_create_users(
            self,
            interface: str,
            users: List[BulkUserItem],
    ):
        created = skipped = 0
        errors = []

        allowed_interfaces = {"driver", "courier"}
        if interface not in allowed_interfaces:
            raise ValueError(f"interface must be one of {allowed_interfaces}")

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for idx, user in enumerate(users):
                    try:
                        payload = {
                            "phone": user.phone,
                            "group_names": [interface],
                        }
                        if user.external_id is not None:
                            payload["profile"] = {"external_id": user.external_id}

                        json_payload = maybe_json_dumps(payload)

                        row = await conn.fetchrow(
                             "SELECT status, user_id FROM accounts.create_user_bulk_stub($1::jsonb)",
                            json_payload,
                        )

                        if row["status"] == "created":
                            created += 1
                        elif row["status"] == "skipped":
                            skipped += 1
                        else:
                            errors.append({
                                "index": idx,
                                "phone": user.phone,
                                "reason": f"unexpected status: {row['status']}"
                            })

                    except Exception as e:
                        errors.append({
                            "index": idx,
                            "phone": user.phone,
                            "reason": str(e)
                        })

        return {"created": created, "skipped": skipped, "errors": errors}

    async def get_paginated(self, page: int, size: int) -> PaginatedResponse[UserReadExtended]:
        """
        Возвращает пагинированный список пользователей с агрегированными контактами и группами.
        Использует PostgreSQL-функцию accounts.get_users_with_relations.
        """
        if page < 1 or size < 1:
            raise ValueError("page и size должны быть >= 1")
        if size > 100:
            raise ValueError("size не может быть больше 100")

        offset = (page - 1) * size

        rows = await self.pool.fetch(
            "SELECT * FROM accounts.get_users_with_relations($1, $2)",
            size, offset
        )

        total = await self.pool.fetchval("SELECT accounts.count_users()")

        items = []
        for row in rows:
            d = dict(row)
            # profile может быть JSONB → приводим к dict
            d["profile"] = maybe_json_loads(d.get("profile"))
            # contacts и groups уже приходят в правильном формате из БД
            items.append(UserReadExtended(**d))

        pages = (total + size - 1) // size
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

def get_user_service(pool: Pool = Depends(get_accounts_db_pool_dep)) -> UserService:
    return UserService(pool)


async def bulk_create_users_from_file(file: UploadFile) -> UploadResult:
    """
    Обрабатывает загруженный файл с колонками: phone, user_groups.
    Пример user_groups: "client,driver"
    Возвращает статистику по обработке.
    """
    required_columns = {"phone", "user_groups"}
    rows = await read_file_to_dicts(file, required_columns=required_columns)

    success_count = 0
    errors: List[str] = []

    for idx, raw_row in enumerate(rows, start=2):  # строка 1 — заголовок
        try:
            # Валидация через Pydantic
            validated = UserBulkCreateRow(**raw_row)

            # Парсим группы
            groups = [g.strip() for g in validated.user_groups.split(",") if g.strip()]
            if not groups:
                raise ValueError("Поле user_groups не содержит валидных групп")

            # 🔜 Здесь будет вызов PostgreSQL-функции, например:
            # await assign_groups_by_phone(validated.phone, groups)
            logger.debug(f"Привязка групп {groups} к телефону {validated.phone}")
            success_count += 1

        except Exception as e:
            phone_display = raw_row.get("phone", "N/A")
            errors.append(f"строка {idx} (phone='{phone_display}'): {str(e)}")

    return UploadResult(
        success_count=success_count,
        error_count=len(errors),
        errors=errors
    )
