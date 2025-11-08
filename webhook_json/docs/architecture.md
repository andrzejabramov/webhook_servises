# Архитектура проекта: Webhook + User Management

## 🎯 Цель
- Приём вебхуков → сохранение в **legacy-БД `paydb`** (с JSONB, без изменений).
- Управление учётными группами → в **новой БД `mydb`** (чистая, типизированная, без JSONB).
- Полная изоляция двух потоков данных.
- Готовность к расширению: авторизация, кэш, rate-limit — без переписывания ядра.

---

## 🌐 Общая структура
src/  
├── main.py # Точка входа, lifespan, подключение роутов  
├── settings.py # Pydantic-настройки (2 БД, RabbitMQ, логи)  
├── routers/  
│ ├── init.py  
│ ├── webhook.py # Роут: POST /webhook → paydb  
│ └── accounts/ # CRUD для user_groups → mydb  
│ └── init.py  
├── dependencies/ # DI через FastAPI Depends  
│ ├── init.py  
│ ├── db.py # Пулы подключений к БД  
│ └── webhook.py # Логика обработки вебхука  
├── services/ # Бизнес-логика  
│ ├── init.py  
│ ├── accounts.py # UserGroupService  
│ ├── db_service.py # Вызов PostgreSQL-функций  
│ └── logger_config.py # Настройка loguru  
├── schemas/ # Pydantic-модели  
│ ├── init.py  
│ ├── accounts.py # UserGroupCreate/Read/Update  
│ └── webhook.py # WebhookPayload (extra="allow")  
├── db/ # Работа с БД  
│ ├── init.py  
│ ├── pools.py # Управление пулами asyncpg  
│ └── functions.py # Вызов функций в paydb  
├── exceptions/ # Кастомные HTTP-исключения  
│ ├── init.py  
│ └── exceptions.py  
└── queue/ # Заготовка под RabbitMQ (пока пусто)  


---

## ⚙️ Настройки: `.env` и `Settings`

### `.env`
```env
DATABASE_URL=postgresql://my_login:my_pass@localhost:5432/paydb   # legacy
MYDB_DSN=postgresql://my_login:my_pass@localhost:5432/mydb        # новая архитектура
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
LOG_DIR=./logs
```

### src/settings.py
```commandline
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Legacy: для вебхуков
    database_url: PostgresDsn

    # Новая архитектура: для учётных записей
    mydb_dsn: PostgresDsn

    rabbitmq_url: str
    log_dir: Path = Path("./logs")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "forbid"  # ← все переменные должны быть объявлены!
    }

settings = Settings()
```

### 🗃 Базы данных

| БД      | Назначение           | Схема     | Таблицы                     |
|--------|----------------------|----------|----------------------------|
| `paydb` | Приём вебхуков       | `to_can` | с JSONB (legacy)           |
| `mydb`  | Учётные записи       | `accounts` | `users`, `user_groups`     |

### Таблица accounts.user_groups (в mydb)

```commandline
CREATE TABLE accounts.user_groups (
  id int2 GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name text NOT NULL UNIQUE,
  description text,
  is_active bool NOT NULL DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
```

❌ Нет JSONB — только типизированные поля.  
✅ is_active вместо удаления.  
✅ Триггер updated_at.  

## 🔄 Поток данных

### 1. Вебхук → paydb

```commandline
POST /webhook 
  → schemas.WebhookPayload 
  → dependencies.webhook.process_webhook_payload 
  → services.db_service.call_webhook_function 
  → PostgreSQL: to_can.f_syspay(payload::json)
```

### 2. Управление группами → mydb

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
✅ Полная изоляция: вебхук не может случайно записать в mydb. 

## 🧪 Роуты и зависимости

### Вебхук

```commandline
# routers/webhook.py
@router.post("")
async def get_hook(result = Depends(process_webhook_payload)):
    return result
```

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

### Как добавить новый функционал без нарушения ядра?

| Фича                 | Где добавить                          | Не затрагивает            |
|----------------------|---------------------------------------|---------------------------|
| Авторизация          | `dependencies/auth.py` + `Depends()`   | `services/`, `db/`        |
| Кэширование          | `services/cache.py` + Redis-пул       | Роуты, схемы              |
| RabbitMQ-публикация  | `queue/publisher.py`                  | БД, настройки             |
| Аудит действий       | Новый сервис + таблица в `mydb`       | Вебхук, legacy            |

Принцип: новый функционал — новый модуль, старый код остаётся неизменным. 

## ▶️ Как запустить

```commandline
python3 -m src.main
```

Swagger UI: http://localhost:8000/docs   
Логи: ./logs/webhook.log

### ✅ Следующие шаги (опционально)

1. Реализовать accounts.get_user_group(id) и другие функции в PostgreSQL.  
2. Добавить валидацию name (min/max length, regex).  
3. Подключить RABBITMQ_URL для публикации событий.  
4. Добавить middleware для логирования запросов.  

---

Этот документ:
- **Фиксирует текущее состояние** проекта,
- **Объясняет архитектурные решения**,
- **Гарантирует масштабируемость** без технического долга.

Ты можешь сохранить его в репозиторий и использовать как **живую документацию**.



