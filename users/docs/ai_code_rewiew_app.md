### /src/db/pools.py
```commandline
from asyncpg import Pool, create_pool

from src.settings import settings

# Глобальные пулы (можно добавить другие: analytics_pool, auth_pool и т.д.)
_accounts_db_pool: Pool | None = None

async def init_pools():
    global _accounts_db_pool
    if _accounts_db_pool is None:
        _accounts_db_pool = await create_pool(dsn=str(settings.mydb_dsn))

async def close_pools():
    global _accounts_db_pool
    if _accounts_db_pool:
        await _accounts_db_pool.close()
        _accounts_db_pool = None

def get_accounts_db_pool() -> Pool:  # ← новая функция
    if _accounts_db_pool is None:
        raise RuntimeError("Accounts DB pool not initialized")
    return _accounts_db_pool
```

### /src/dependencies/db.py
```commandline
from asyncpg import Pool

from src.db.pools import get_accounts_db_pool


def get_accounts_db_pool_dep() -> Pool:  # ← новая зависимость
    """Для учётных записей → mydb"""
    return get_accounts_db_pool()
```

### /src/exceptions/exceptions.py
```commandline
from fastapi import HTTPException


class DatabaseError(HTTPException):
    def __init__(self, detail: str = "Database unavailable"):
        super().__init__(status_code=503, detail=detail)
```

### /src/queue/comnection.py
```commandline

```
### /src/queue/publisher.py
```commandline

```

### /src/routers/accounts/__init__.py
```commandline
from fastapi import APIRouter
from .user_groups import router as user_groups_router
from .users import router as users_router
from .user_group_memberships import router as memberships_router
from .user_contacts import router as user_contacts_router
from .contact_types import router as contact_types_router

# Создаём общий роутер для всего модуля "accounts"
router = APIRouter()

# Подключаем подмодули с их внутренними префиксами
router.include_router(user_groups_router, prefix="/user-groups")
router.include_router(users_router)
router.include_router(memberships_router)
router.include_router(user_contacts_router)
router.include_router(contact_types_router)

```

### /src/routers/accounts/contact_types.py
```commandline
from fastapi import APIRouter, Depends, status
from asyncpg import Pool

from src.dependencies.db import get_accounts_db_pool_dep
from src.services.contact_types import ContactTypeService
from src.schemas.contact_types import ContactTypeCreate, ContactTypeRead

router = APIRouter(prefix="/accounts/contact-types", tags=["Accounts: Contact Types"])

def get_contact_type_service(pool: Pool = Depends(get_accounts_db_pool_dep)) -> ContactTypeService:
    return ContactTypeService(pool)

@router.post("/", response_model=ContactTypeRead, status_code=status.HTTP_201_CREATED)
async def create_contact_type(
    data: ContactTypeCreate,
    service: ContactTypeService = Depends(get_contact_type_service)
):
    return await service.create(data)

@router.get("/", response_model=list[ContactTypeRead])
async def list_contact_types(
    service: ContactTypeService = Depends(get_contact_type_service)
):
    return await service.list_all()
```

### /src/routers/accounts/user_contacts.py
```commandline
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from asyncpg import Pool
from typing import List

from src.dependencies.db import get_accounts_db_pool_dep
from src.services.user_contacts import UserContactService
from src.schemas.user_contacts import UserContactCreate, UserContactRead


router = APIRouter(prefix="/accounts/contacts", tags=["Accounts: User Contacts"])


async def get_contact_service(pool: Pool = Depends(get_accounts_db_pool_dep)) -> UserContactService:
    return UserContactService(pool)

@router.post("/", response_model=UserContactRead, status_code=status.HTTP_201_CREATED)
async def create_user_contact(
    contact: UserContactCreate,
    service: UserContactService = Depends(get_contact_service)
):
    return await service.create(contact)
```

### /src/routers/accounts/user_group_memberships.py
```commandline
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from asyncpg import Pool
from typing import List

from src.dependencies.db import get_accounts_db_pool_dep
from src.services.user_group_memberships import UserGroupMembershipService
from src.schemas.user_group_memberships import (
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
```

### /src/routers/accounts/user_groups.py
```commandline
from fastapi import APIRouter, Depends, HTTPException, status, Body
from asyncpg import Pool

from src.services.user_groups import UserGroupService
from src.schemas.user_groups import UserGroupCreate, UserGroupUpdate, UserGroupRead
from src.dependencies.db import get_accounts_db_pool_dep  # ← должен возвращать Pool из app.state.db_pool


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
```

### /src/routers/accounts/users.py
```commandline
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
```

### /src/schemas/contact_types.py
```commandline
from pydantic import BaseModel, UUID4, Field
from datetime import datetime


class ContactTypeBase(BaseModel):
    name: str

class ContactTypeCreate(ContactTypeBase):
    pass

class ContactTypeRead(ContactTypeBase):
    id: int
    created_at: datetime
```

### /src/schemas/user_contacts.py
```commandline
from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class UserContactBase(BaseModel):
    user_id: UUID
    contact_type_id: int
    value: str

class UserContactCreate(UserContactBase):
    pass

class UserContactRead(UserContactBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserContactDeactivate(BaseModel):
    is_active: bool = False
```

### /src/schemas/user_group_memberships.py
```commandline
from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class UserGroupMembershipBase(BaseModel):
    user_id: UUID
    group_id: int  # int2 в PostgreSQL → int в Python

class UserGroupMembershipCreate(UserGroupMembershipBase):
    pass

class UserGroupMembershipRead(UserGroupMembershipBase):
    is_active: bool
    deactivated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # для Pydantic v2 (ранее orm_mode)

class UserGroupMembershipUpdate(BaseModel):
    is_active: bool
```

### /src/schemas/user_groups.py
```commandline
from pydantic import BaseModel, UUID4, Field
from typing import Optional
from datetime import datetime


class UserGroupBase(BaseModel):
    name: str
    description: Optional[str] = None

class UserGroupCreate(UserGroupBase):
    pass

class UserGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = {
                "is_active": False
            }

class UserGroupRead(UserGroupBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```

### /src/schemas/users.py
```commandline
from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    is_active: Optional[bool] = None
    profile: Optional[Dict[str, Any]] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    profile: Optional[Dict[str, Any]] = None

class UserRead(UserBase):
    id: UUID
    username: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    profile: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}
```

### /src/services/contact_types.py
```commandline
from asyncpg import Pool
from typing import List

from src.utils.json_utils import normalize_user_row, maybe_json_dumps, maybe_json_loads
from src.schemas.contact_types import ContactTypeCreate, ContactTypeRead


class ContactTypeService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def list_all(self) -> List[ContactTypeRead]:
        query = 'SELECT * FROM accounts.list_contact_types()'
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
        return [ContactTypeRead(**dict(row)) for row in rows]

    async def create(self, data: ContactTypeCreate) -> ContactTypeRead:
        query = 'SELECT * FROM accounts.create_contact_type($1)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, data.name)
        return ContactTypeRead(**dict(row))
```

### /src/services/user_contacts.py
```commandline
from asyncpg import Pool
from typing import List, Optional
from uuid import UUID

from src.utils.json_utils import normalize_user_row, maybe_json_dumps, maybe_json_loads
from src.schemas.user_contacts import UserContactCreate, UserContactRead


class UserContactService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def create(self, contact: UserContactCreate) -> UserContactRead:
        query = 'SELECT * FROM accounts.create_user_contact($1, $2, $3)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, contact.user_id, contact.contact_type_id, contact.value)
        return UserContactRead(**dict(row))

    async def get_by_id(self, contact_id: UUID) -> Optional[UserContactRead]:
        query = 'SELECT * FROM accounts.get_user_contact_by_id($1)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, contact_id)
        return UserContactRead(**dict(row)) if row else None

    async def get_by_user_id(self, user_id: UUID, only_active: bool = True) -> List[UserContactRead]:
        query = 'SELECT * FROM accounts.get_user_contacts_by_user_id($1, $2)'
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, user_id, only_active)
        return [UserContactRead(**dict(row)) for row in rows]

    async def deactivate(self, contact_id: UUID) -> UserContactRead:
        query = 'SELECT * FROM accounts.deactivate_user_contact($1)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, contact_id)
        return UserContactRead(**dict(row))

    async def reactivate(self, contact_id: UUID) -> UserContactRead:
        query = 'SELECT * FROM accounts.reactivate_user_contact($1)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, contact_id)
        return UserContactRead(**dict(row))
```

### /src/services/user_group_memberships.py
```commandline
from asyncpg import Pool
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.utils.json_utils import normalize_user_row, maybe_json_dumps, maybe_json_loads
from src.schemas.user_group_memberships import UserGroupMembershipCreate, UserGroupMembershipRead, UserGroupMembershipUpdate


class UserGroupMembershipService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def create(self, membership: UserGroupMembershipCreate) -> UserGroupMembershipRead:
        query = 'SELECT * FROM accounts.create_user_group_membership($1, $2)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, membership.user_id, membership.group_id)
        return UserGroupMembershipRead(**dict(row))

    async def get(self, user_id: UUID, group_id: int) -> Optional[UserGroupMembershipRead]:
        query = 'SELECT * FROM accounts.get_user_group_membership($1, $2)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id, group_id)
        return UserGroupMembershipRead(**dict(row)) if row else None

    async def get_user_groups(self, user_id: UUID, only_active: bool = True) -> List[UserGroupMembershipRead]:
        query = 'SELECT * FROM accounts.get_user_groups($1, $2)'
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, user_id, only_active)
        return [UserGroupMembershipRead(**dict(row)) for row in rows]

    async def deactivate(self, user_id: UUID, group_id: int) -> UserGroupMembershipRead:
        query = 'SELECT * FROM accounts.deactivate_user_group_membership($1, $2)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id, group_id)
        return UserGroupMembershipRead(**dict(row))

    async def reactivate(self, user_id: UUID, group_id: int) -> UserGroupMembershipRead:
        query = 'SELECT * FROM accounts.reactivate_user_group_membership($1, $2)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id, group_id)
        return UserGroupMembershipRead(**dict(row))
```

### /src/services/user_groups.py
```commandline
from asyncpg import Pool
from typing import List, Optional

from src.utils.json_utils import normalize_user_row, maybe_json_dumps, maybe_json_loads
from src.schemas.user_groups import UserGroupCreate, UserGroupUpdate, UserGroupRead


class UserGroupService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def create(self, group: UserGroupCreate) -> UserGroupRead:
        query = 'SELECT * FROM accounts.create_user_group($1, $2)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, group.name, group.description)
        return UserGroupRead(**dict(row))

    async def get_all(self) -> List[UserGroupRead]:
        query = 'SELECT * FROM accounts.list_user_groups()'
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
        return [UserGroupRead(**dict(row)) for row in rows]

    async def update(self, group_id: int, group: UserGroupUpdate) -> Optional[UserGroupRead]:
        query = 'SELECT * FROM accounts.update_user_group($1, $2, $3, $4)'
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                group_id,
                group.name,  # может быть None
                group.description,  # может быть None
                group.is_active  # может быть None
            )
        return UserGroupRead(**dict(row)) if row else None
```

### /src/services/users.py
```commandline
from asyncpg import Pool
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.utils.json_utils import normalize_user_row, maybe_json_dumps, maybe_json_loads
from src.schemas.users import UserCreate, UserUpdate, UserRead


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
```

### /src/logger_config.py
```commandline
from pathlib import Path
from loguru import logger

from src.settings import settings


def setup_logger():
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.remove()

    # Лог в файл (ежедневная ротация, 6 месяцев, архивация)
    logger.add(
        log_dir / "users.logs",
        rotation="00:00",
        retention="180 days",
        compression="zip",
        level="INFO",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )

    # Ошибки в stderr (для Docker-логов)
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level="ERROR"
    )

    return logger
```

### /src/main.py
```commandline
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.db.pools import init_pools, close_pools
from src.routers.accounts import router as accounts_router
from src.settings import settings
from src.logger_config import setup_logger


logger = setup_logger()
logger.info("✅ Logger is configured and working")

@asynccontextmanager
async def lifespan(app):
    await init_pools()
    yield
    await close_pools()


app = FastAPI(lifespan=lifespan)
app.include_router(accounts_router, prefix="/accounts")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
```

### /src/settings.py
```commandline
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, PostgresDsn
from pathlib import Path


class Settings(BaseSettings):
    mydb_dsn: PostgresDsn
    rabbitmq_url: str
    log_dir: Path = Path("./logs")

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",  # рекомендуется явно указать кодировку
        extra="forbid",  # или "ignore", но по умолчанию — "ignore"
    )


settings = Settings()
```


