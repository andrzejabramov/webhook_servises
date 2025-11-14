

## 1. Управление группами → mydb

```commandline
POST /accounts/user-groups 
  → schemas.UserGroupCreate 
  → UserGroupService.create() 
  → PostgreSQL: accounts.create_user_group(name, description)
```

## 🧩 Управление подключениями к БД

### src/db/pools.py

```commandline
# Два независимых пула:
_main_db_pool      # → paydb (вебхуки)
_accounts_db_pool  # → mydb (учётные записи)

# Инициализация:
await init_pools()      # создаёт оба
await close_pools()     # закрывает оба
```

### src/dependencies/db.py

```commandline
def get_db_pool() -> Pool:             # → paydb
def get_accounts_db_pool_dep() -> Pool # → mydb
```

## 🧪 Роуты и зависимости

### Учётные группы

```commandline
# routers/accounts.py
@router.post("/", response_model=UserGroupRead)
async def create_group(
    group: UserGroupCreate,
    service: UserGroupService = Depends(get_service)  # ← использует mydb
):
    return await service.create(group)
```

## 🛡 Обработка ошибок

### Кастомные исключения (src/exceptions/exceptions.py)

WebhookProcessingError → 500  
InvalidWebhookData → 400    
DatabaseError → 503  
Логируются через loguru с ротацией и архивацией.   

## 📦 Готовность к расширению

```commandline
python3 -m src.main
```

Swagger UI: http://localhost:8000/docs   
Логи: ./logs/webhook.log
