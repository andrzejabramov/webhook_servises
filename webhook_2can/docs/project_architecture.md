## 📁 Структура проекта webhook_2can

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

## 💡 Особенности, соответствующие стилю
Чёткое разделение слоёв: роут → сервис → БД/очередь.  
Асинхронность через async/await и asyncpg/aio_pika.  
DTO через Pydantic, без ORM.  
Конфигурация через .env, безопасная загрузка в settings.py.  
Логирование в файлы (./logs/), легко интегрируется с Logrotate.  
Docker и оркестрация через docker-compose.yml из корня payment_services.  

