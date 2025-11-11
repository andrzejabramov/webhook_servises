from fastapi import APIRouter
from .user_groups import router as user_groups_router
from .users import router as users_router
from .user_group_memberships import router as memberships_router
from .user_contacts import router as user_contacts_router

# Создаём общий роутер для всего модуля "accounts"
router = APIRouter()

# Подключаем подмодули с их внутренними префиксами
router.include_router(user_groups_router, prefix="/user-groups")
router.include_router(users_router)
router.include_router(memberships_router)
router.include_router(user_contacts_router)
