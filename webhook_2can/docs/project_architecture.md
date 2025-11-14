## 📁 Структура проекта webhook_2can

### 🎯 Цель
- Приём вебхуков → сохранение в **legacy-БД `paydb`** (с JSONB, без изменений).
- Управление учётными группами → в **новой БД `mydb`** (чистая, типизированная, без JSONB).
- Полная изоляция двух потоков данных.
- Готовность к расширению: авторизация, кэш, rate-limit — без переписывания ядра.

---

webhook_2can/  
├── .venv/                          # Виртуальное окружение Python (не коммитится)  
├── docs/  
│   ├── structure_project.md        # Общая структура проекта (как этот документ)  
│   └── structure_app.md            # Архитектура приложения: поток данных, компоненты  
├── src/  
│   ├── __init__.py  
│   ├── main.py                     # Точка входа FastAPI-приложения  
│   ├── settings.py                 # Настройки из .env (с pydantic.BaseSettings)  
│   ├── logger_config.py            # Конфигурация Loguru (лог-файлы в ./logs)  
│   │  
│   ├── db/  
│   │   ├── __init__.py  
│   │   ├── functions.py            # Обёртки для вызова PostgreSQL-функций (например, to_can.f_payment)  
│   │   └── pools.py                # Создание и управление пулом asyncpg-соединений  
│   │  
│   ├── dependencies/  
│   │   ├── __init__.py  
│   │   ├── db.py                   # FastAPI-зависимость: get_db_pool → для внедрения в эндпоинты  
│   │   └── webhook.py              # Специфичные зависимости (если понадобятся)  
│   │  
│   ├── exceptions/  
│   │   ├── __init__.py  
│   │   └── exceptions.py           # Кастомные исключения (например, WebhookValidationError)  
│   │  
│   ├── queue/  
│   │   ├── __init__.py  
│   │   ├── connection.py           # Асинхронное подключение к RabbitMQ (aio_pika)  
│   │   └── publisher.py            # Функции публикации сообщений в обменники/очереди  
│   │  
│   ├── routers/  
│   │   ├── __init__.py  
│   │   └── webhook.py              # Роутер FastAPI: POST /webhook/2can/  
│   │  
│   ├── schemas/  
│   │   ├── __init__.py  
│   │   └── webhook.py              # Pydantic DTO: входящие и исходящие схемы (валидация JSON)    
│   │  
│   └── services/  
│       ├── __init__.py  
│       └── db_service.py           # Бизнес-логика: вызов db.functions, обработка ошибок, трансформация данных      
│      
├── .env                            # Переменные окружения (не в Git)      
├── .env.example                    # Пример .env для разработчиков      
├── .gitignore                      # Исключает .venv, .env, __pycache__, logs/ и т.д.  
├── Dockerfile                      # Сборка образа (копирует src/, устанавливает зависимости)  
└── requirements.txt                # Зависимости: fastapi, asyncpg, aio_pika, loguru, pydantic, uvicorn и др.  

## 📝 Описание ключевых компонентов

### src/main.py
Создаёт FastAPI-приложение.  
Подключает роутер webhook.  
Инициализирует логгер (logger_config.py).  
Может включать middleware (CORS, логирование запросов).  

### src/settings.py  
Использует pydantic.BaseSettings для загрузки:  
DATABASE_URL (для main-БД),  
RABBITMQ_URL,  
LOG_DIR (по умолчанию ./logs),  
APP_ENV и др.  

### src/db/pools.py
create_pool() → создаёт пул asyncpg.Pool.  
Используется в зависимостях и сервисах.  

### src/db/functions.py
Асинхронные функции-обёртки:  
```commandline
async def call_f_payment(pool: asyncpg.Pool, payload: dict) -> Any:
    return await pool.fetchval('SELECT "to_can"."f_payment"($1)', json.dumps(payload))
```

### src/services/db_service.py  
Основная логика обработки:  
получает валидированный DTO из роута,  
вызывает нужную PostgreSQL-функцию,  
при успехе — публикует событие в RabbitMQ через queue.publisher.  

### src/routers/webhook.py  
Минималистичный эндпоинт:  
```commandline
@router.post("/webhook/2can/", status_code=200)
async def handle_webhook(
    payload: WebhookSchema,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    await db_service.process_webhook(payload, pool)
    return {"status": "accepted"}
```

```commandline
# routers/webhook.py
@router.post("")
async def get_hook(result = Depends(process_webhook_payload)):
    return result
```

### src/schemas/webhook.py   
Pydantic-модели:  
WebhookSchema — с 5 обязательными полями, остальные Optional.  
Поддерживает валидацию и сериализацию.  

### src/queue/publisher.py
```commandline
publish_payment_event(event_data: dict) → отправляет в очередь payment.processed.  
```

### src/exceptions/exceptions.py
Например:  
```commandline
class WebhookValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)
```

### src/logger_config.py
Настраивает Loguru: ротация логов, формат, вывод в ./logs/webhook_2can.log.  

### Dockerfile
Использует python:3.11-slim.  
Копирует requirements.txt и src/.  
Запускает через uvicorn src.main:app --host 0.0.0.0 --port 8000.  

### ⚙️ Настройки: `.env` и `Settings`

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

### 🔄 Поток данных

### 1. Вебхук → paydb

```commandline
POST /webhook 
  → schemas.WebhookPayload 
  → dependencies.webhook.process_webhook_payload 
  → services.db_service.call_webhook_function 
  → PostgreSQL: to_can.f_syspay(payload::json)
```
### 🧩 Управление подключениями к БД

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

### 🛡 Обработка ошибок

### Кастомные исключения (src/exceptions/exceptions.py)

WebhookProcessingError → 500  
InvalidWebhookData → 400    
DatabaseError → 503  
Логируются через loguru с ротацией и архивацией.   

### ▶️ запуск:

```commandline
python3 -m src.main
```

### Swagger UI: http://localhost:8000/docs   
### Логи: ./logs/webhook.log

### Этот документ:
- **Фиксирует текущее состояние** проекта,
- **Объясняет архитектурные решения**,
- **Гарантирует масштабируемость** без технического

## 💡 Особенности, соответствующие стилю
Чёткое разделение слоёв: роут → сервис → БД/очередь.  
Асинхронность через async/await и asyncpg/aio_pika.  
DTO через Pydantic, без ORM.  
Конфигурация через .env, безопасная загрузка в settings.py.  
Логирование в файлы (./logs/), легко интегрируется с Logrotate.  
Docker и оркестрация через docker-compose.yml из корня payment_services.  

