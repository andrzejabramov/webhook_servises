🎯 Цель
Создать:

2 PostgreSQL-ноды: pg-node-1 (мастер), pg-node-2 (реплика)  
etcd — для координации (DCS)    
Patroni — в каждом PG-контейнере (управляет ролями)  
HAProxy — маршрутизация:  
:5432 → только запись (мастер)  
:5433 → только чтение (реплика → fallback на мастер)  
Сервисы (users, auth, webhook) подключаются к HAProxy  
В случае падения мастера → реплика становится мастером, бывший мастер — репликой  
📋 План работ  
🔹 Шаг 1. Подготовка структуры проекта  
```bash
payment_servises/
├── pg-node/
│   ├── Dockerfile
│   └── patroni.yml
├── haproxy/
│   └── haproxy.cfg
└── docker-compose.yml  # ← обновим этот файл
```

---

### 🔹 Шаг 2. **Создай `pg-node/Dockerfile`**
```dockerfile
# pg-node/Dockerfile
FROM postgres:16

# Установка Patroni и etcd-клиента
RUN apt-get update && apt-get install -y python3-pip curl && \
    pip3 install patroni[etcd] && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Копируем конфиг Patroni (он будет монтироваться через volume)
WORKDIR /etc/patroni
COPY patroni.yml .

# Запускаем Patroni вместо PostgreSQL
CMD ["patroni", "/etc/patroni/patroni.yml"]
```

---

### 🔹 Шаг 3. **Создай базовый `pg-node/patroni.yml`**
```yaml
# pg-node/patroni.yml (общий шаблон)
scope: users_cluster
namespace: /db/
name: pg-node-X  # ← будет переопределяться в docker-compose

restapi:
  listen: 0.0.0.0:8008
  connect_address: pg-node-X:8008

etcd:
  host: etcd:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
    postgresql:
      use_pg_rewind: true
      use_slots: true
      parameters:
        wal_level: replica
        hot_standby: "on"
        max_wal_senders: 10
        wal_keep_size: 128MB
        max_replication_slots: 10

postgresql:
  listen: 0.0.0.0:5432
  connect_address: pg-node-X:5432
  data_dir: /var/lib/postgresql/data/pgdata
  bin_dir: /usr/lib/postgresql/16/bin
  authentication:
    replication:
      username: replicator
      password: repPass123
    superuser:
      username: postgres
      password: mysecretpassword
  parameters:
    shared_preload_libraries: pg_stat_statements
```

> ⚠️ `name` и `connect_address` будут переопределяться для каждой ноды через environment в `docker-compose`.  

---

### 🔹 Шаг 4. **Обнови `docker-compose.yml`**

```yaml
version: '3.8'

services:
  # --- DCS: etcd ---
  etcd:
    image: bitnami/etcd:latest
    environment:
      - ALLOW_NONE_AUTHENTICATION=yes
      - ETCD_LISTEN_CLIENT_URLS=http://0.0.0.0:2379
      - ETCD_ADVERTISE_CLIENT_URLS=http://etcd:2379
    networks:
      - backend

  # --- PostgreSQL Node 1 (мастер/реплика) ---
  pg-node-1:
    build: ./pg-node
    environment:
      PATRONI_NAME: pg-node-1
      PATRONI_RESTAPI_CONNECT_ADDRESS: pg-node-1:8008
      PATRONI_POSTGRESQL_CONNECT_ADDRESS: pg-node-1:5432
    volumes:
      - pgdata1:/var/lib/postgresql/data
    networks:
      - backend
    depends_on:
      - etcd

  # --- PostgreSQL Node 2 (реплика/мастер) ---
  pg-node-2:
    build: ./pg-node
    environment:
      PATRONI_NAME: pg-node-2
      PATRONI_RESTAPI_CONNECT_ADDRESS: pg-node-2:8008
      PATRONI_POSTGRESQL_CONNECT_ADDRESS: pg-node-2:5432
    volumes:
      - pgdata2:/var/lib/postgresql/data
    networks:
      - backend
    depends_on:
      - etcd

  # --- HAProxy: маршрутизация ---
  haproxy:
    image: haproxytech/haproxy-alpine
    ports:
      - "5432:5432"  # write
      - "5433:5433"  # read
    volumes:
      - ./haproxy/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg
    networks:
      - backend
    depends_on:
      - pg-node-1
      - pg-node-2

  # --- Остальные сервисы подключаются к HAProxy ---
  redis:
    image: redis:7-alpine
    networks: [backend]

  rabbitmq:
    image: rabbitmq:3.13-management
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    networks: [backend]

  auth:
    build: ./auth
    ports: ["8001:8001"]
    environment:
      POSTGRES_HOST: haproxy
      POSTGRES_PORT: "5432"  # ← запись
      REDIS_URL: redis://redis:6379/0
    depends_on: [haproxy, redis]
    networks: [backend]

  users:
    build: ./users
    ports: ["8002:8002"]
    environment:
      DATABASE_WRITE_URL: postgresql://postgres:mysecretpassword@haproxy:5432/postgres
      DATABASE_READ_URL: postgresql://postgres:mysecretpassword@haproxy:5433/postgres
    depends_on: [haproxy]
    networks: [backend]

  webhook:
    build: ./webhook_2can
    ports: ["8000:8000"]
    environment:
      DATABASE_WRITE_URL: postgresql://postgres:mysecretpassword@haproxy:5432/postgres
      DATABASE_READ_URL: postgresql://postgres:mysecretpassword@haproxy:5433/postgres
    depends_on: [haproxy]
    networks: [backend]

volumes:
  pgdata1:
  pgdata2:
  postgres_data:  # можно удалить, больше не нужен

networks:
  backend:
    driver: bridge
```

---

### 🔹 Шаг 5. **Создай `haproxy/haproxy.cfg`**

```cfg
global
    maxconn 1000

defaults
    timeout connect 5s
    timeout client 30s
    timeout server 30s
    mode tcp

# --- Запись: только мастер ---
frontend write_frontend
    bind *:5432
    default_backend write_backend

backend write_backend
    option pgsql-check user postgres
    server pg-node-1 pg-node-1:5432 check
    server pg-node-2 pg-node-2:5432 check backup

# --- Чтение: реплика → мастер (fallback) ---
frontend read_frontend
    bind *:5433
    default_backend read_backend

backend read_backend
    option pgsql-check user postgres
    server pg-node-2 pg-node-2:5432 check
    server pg-node-1 pg-node-1:5432 check backup
```

> 💡 HAProxy не знает, кто мастер, но Patroni гарантирует, что **только мастер принимает запись**.
> Для чтения мы явно делаем `pg-node-2` primary, `pg-node-1` — backup.

---

### 🔹 Шаг 6. **Настрой пулы подключений в `users` и `webhook`**

В `users/src/settings.py` добавь:
```python
database_write_url: PostgresDsn
database_read_url: PostgresDsn
```

В `users/.env`:
```env
database_write_url=postgresql://postgres:mysecretpassword@haproxy:5432/postgres
database_read_url=postgresql://postgres:mysecretpassword@haproxy:5433/postgres
```

В коде создай два пула:
```python
# src/db/pools.py
write_pool = await asyncpg.create_pool(settings.database_write_url)
read_pool = await asyncpg.create_pool(settings.database_read_url)
```

И используй:
- `write_pool` — в `POST`, `PATCH`
- `read_pool` — в `GET`

---

### 🔹 Шаг 7. **Инициализация схем**

1. Запусти стек:
   ```bash
   docker-compose up --build
   ```
2. Подключиcь к мастеру (обычно `pg-node-1`):
   ```bash
   docker exec -it payment_servises-pg-node-1-1 psql -U postgres
   ```
3. Выполни миграции (создай схему `accounts`, таблицы, функции, типы и т.д.) — **только на мастере**.
4. Patroni автоматически синхронизирует реплику.

> 📌 **Не заполняй реплику вручную!** Только мастер принимает DDL/DML.

---

### 🔹 Шаг 8. **Тестирование отказоустойчивости**

1. **Останови мастер**:
   ```bash
   docker stop payment_servises-pg-node-1-1
   ```
2. Через ~30 сек Patroni выберет `pg-node-2` как нового мастера.
3. HAProxy продолжит работать:
   - `:5432` → теперь `pg-node-2`
   - `:5433` → `pg-node-2` (и fallback на `pg-node-1`, но он выключен)
4. Запусти бывший мастер:
   ```bash
   docker start payment_servises-pg-node-1-1
   ```
5. Он автоматически станет **репликой**.

---

## ✅ Итог

Ты получишь:
- Полноценный HA-кластер PostgreSQL на локалке
- Автоматический failover и восстановление
- Разделение нагрузки: запись → 1 нода, чтение → другая
- Готовность к production (паттерн масштабируется на bare metal / VM)

---

Готов помочь:
- сгенерировать готовые файлы (`Dockerfile`, `patroni.yml`, `haproxy.cfg`),
- адаптировать пулы подключений в `users`,
- написать скрипт инициализации схем.

Нужно?

### USER
Да, сделай эти пункты: Готов помочь:

сгенерировать готовые файлы (Dockerfile, patroni.yml, haproxy.cfg),
адаптировать пулы подключений в users,
написать скрипт инициализации схем. Только еще проясни мне вот что: мы для postgres (Dockerfile), общий docker-compose где все это реализуем в виде кода? Прямо в IDE отдельным проектом? Или как-то по-другому?

### ASSISTANT
Отличный вопрос — давай проясним структуру и рабочий процесс.

---

## 🧭 Где реализуется вся эта архитектура?

**Всё это делается прямо в твоём текущем проекте `payment_servises`**, но **в виде отдельных файлов и сервисов**, встроенных в существующую структуру.

Ты **не создаёшь новый проект**, а **модернизируешь текущий `docker-compose.yml`**, добавляя:
- 2 ноды PostgreSQL вместо одной (`pg-node-1`, `pg-node-2`),
- `etcd`,
- `haproxy`.

---

## 📁 Итоговая структура проекта (внутри `payment_servises/`)

```
payment_servises/
├── docker-compose.yml              ← обновлённый (основной оркестратор)
│
├── pg-node/
│   ├── Dockerfile                  ← кастомный образ с Patroni + PostgreSQL
│   └── patroni.yml                 ← общий шаблон конфига Patroni
│
├── haproxy/
│   └── haproxy.cfg                 ← маршрутизация read/write
│
├── initdb/                         ← скрипты инициализации схем (новая папка)
│   ├── 01_create_extensions.sql
│   ├── 02_create_schema_accounts.sql
│   └── 03_create_functions.sql     ← включая get_user_by_identifier_v1
│
├── auth/                           ← не меняется
├── users/                          ← адаптируем под 2 DSN
├── webhook_2can/                   ← адаптируем под 2 DSN
│
└── .env                            ← можно оставить, но сервисы будут использовать свои .env
```

> ✅ Это **по-прежнему один проект**, просто теперь с HA-кластером PostgreSQL.

---

## 🛠 Что я сейчас сгенерирую (по твоей просьбе)

### 1. **`pg-node/Dockerfile`**
```dockerfile
# pg-node/Dockerfile
FROM postgres:16

# Устанавливаем Patroni и зависимости
RUN apt-get update && \
    apt-get install -y python3-pip curl && \
    pip3 install patroni[etcd] && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем конфиг
COPY patroni.yml /etc/patroni/patroni.yml

# Запускаем Patroni
CMD ["patroni", "/etc/patroni/patroni.yml"]
```

---

### 2. **`pg-node/patroni.yml`**
```yaml
# pg-node/patroni.yml
scope: payment_cluster
namespace: /db/
name: "{{ PATRONI_NAME }}"

restapi:
  listen: 0.0.0.0:8008
  connect_address: "{{ PATRONI_RESTAPI_CONNECT_ADDRESS }}"

etcd:
  host: etcd:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
    postgresql:
      use_pg_rewind: true
      use_slots: true
      parameters:
        wal_level: replica
        hot_standby: "on"
        max_wal_senders: 10
        wal_keep_size: 128MB
        max_replication_slots: 10
        logging_collector: off
        log_destination: stderr

postgresql:
  listen: 0.0.0.0:5432
  connect_address: "{{ PATRONI_POSTGRESQL_CONNECT_ADDRESS }}"
  data_dir: /var/lib/postgresql/data/pgdata
  bin_dir: /usr/lib/postgresql/16/bin
  authentication:
    replication:
      username: replicator
      password: repPass123
    superuser:
      username: postgres
      password: mysecretpassword
  parameters:
    shared_preload_libraries: pg_stat_statements
```

> 💡 `{{ ... }}` — это **Jinja2-шаблон**, который Patroni поддерживает. Переменные подставляются через environment в `docker-compose`.

---

### 3. **`haproxy/haproxy.cfg`**
```cfg
global
    maxconn 2000
    log stdout format raw local0

defaults
    log global
    mode tcp
    timeout connect 5s
    timeout client 30s
    timeout server 30s
    option tcp-check

# --- Запись: только текущий мастер ---
frontend write_frontend
    bind *:5432
    default_backend write_backend

backend write_backend
    option pgsql-check user postgres
    server pg-node-1 pg-node-1:5432 check
    server pg-node-2 pg-node-2:5432 check backup

# --- Чтение: реплика (приоритет), мастер (fallback) ---
frontend read_frontend
    bind *:5433
    default_backend read_backend

backend read_backend
    option pgsql-check user postgres
    server pg-node-2 pg-node-2:5432 check
    server pg-node-1 pg-node-1:5432 check backup
```

---

### 4. **Инициализация схем: `initdb/02_create_schema_accounts.sql`**

> ⚠️ Важно: Patroni **блокирует выполнение `/docker-entrypoint-initdb.d`**, поэтому инициализацию нужно делать **вручную** после запуска кластера (скриптом).

Но для удобства локальной разработки можно использовать **один раз**:

```sql
-- initdb/02_create_schema_accounts.sql
CREATE SCHEMA IF NOT EXISTS accounts;

-- Таблицы, типы, функции...
-- ... (вставь сюда всё, что у тебя уже есть)
```

И выполнить его так:
```bash
# После первого запуска кластера
cat initdb/*.sql | docker exec -i payment_servises-pg-node-1-1 psql -U postgres
```

> 🔁 **Patroni сам синхронизирует схему на реплику**, потому что это DDL передаётся через WAL.

---

### 5. **Адаптация `users`: два пула подключений**

#### `users/src/settings.py`
```python
from pydantic import RedisDsn, PostgresDsn
# ... остальное

class Settings(BaseSettings):
    database_write_url: PostgresDsn
    database_read_url: PostgresDsn
    rabbitmq_url: str
    redis_url: RedisDsn = Field(default="redis://redis:6379/1", alias="REDIS_URL")
    # ...
```

#### `users/.env`
```env
database_write_url=postgresql://postgres:mysecretpassword@haproxy:5432/postgres
database_read_url=postgresql://postgres:mysecretpassword@haproxy:5433/postgres
rabbitmq_url=amqp://guest:guest@rabbitmq:5672/
REDIS_URL=redis://redis:6379/1
```

#### `users/src/db/pools.py`
```python
from asyncpg import create_pool, Pool
from src.settings import settings

write_pool: Pool
read_pool: Pool

async def init_pools():
    global write_pool, read_pool
    write_pool = await create_pool(str(settings.database_write_url))
    read_pool = await create_pool(str(settings.database_read_url))

async def close_pools():
    await write_pool.close()
    await read_pool.close()
```

#### В `users/src/main.py`
```python
@app.on_event("startup")
async def startup():
    await init_pools()

@app.on_event("shutdown")
async def shutdown():
    await close_pools()
```

#### В роутах — зависимость:
```python
# Для записи
def get_write_pool() -> Pool:
    return write_pool

# Для чтения
def get_read_pool() -> Pool:
    return read_pool

# В роуте
@router.get("/by-identifier")
async def get_user(..., pool: Pool = Depends(get_read_pool)):
    ...
```

---

## ✅ Как работать с этим в IDE

1. Открой проект `payment_servises` в PyCharm / VS Code.
2. Создай папки `pg-node/`, `haproxy/`, `initdb/`.
3. Вставь сгенерированные файлы.
4. Обнови `docker-compose.yml` (я могу сгенерировать и его целиком).
5. Запусти:
   ```bash
   docker-compose up --build
   ```
6. После первого запуска — один раз выполни инициализацию схем:
   ```bash
   cat initdb/*.sql | docker exec -i $(docker-compose ps -q pg-node-1) psql -U postgres
   ```

---

Хочешь — сейчас сгенерирую **полный `docker-compose.yml`**, уже интегрированный с твоим текущим стеком (`auth`, `users`, `webhook`, `redis`, `rabbitmq`).

### USER
Да, сгенери пож

### ASSISTANT
Отлично! Ниже — **полный комплект готовых к использованию файлов** для реализации **HA-кластера PostgreSQL с Patroni, etcd, HAProxy и раздельными пулами подключений в `users`**, интегрированный в твою текущую структуру проекта `payment_servises`.

---

## 🗂 Структура проекта после изменений

```
payment_servises/
├── docker-compose.yml                 ← обновлённый
│
├── pg-node/
│   ├── Dockerfile
│   └── patroni.yml
│
├── haproxy/
│   └── haproxy.cfg
│
├── initdb/
│   ├── 01_extensions.sql
│   ├── 02_accounts_schema.sql        ← вставь сюда свои таблицы/функции
│   └── 03_functions.sql              ← например, get_user_by_identifier_v1
│
├── users/
│   ├── .env                          ← обновлён
│   └── src/
│       ├── settings.py               ← обновлён
│       ├── db/pools.py               ← новый файл
│       └── main.py                   ← обновлён
│
└── ...                               ← остальные сервисы без изменений
```

---

## 📄 1. `pg-node/Dockerfile`

```dockerfile
# pg-node/Dockerfile
FROM postgres:16

RUN apt-get update && \
    apt-get install -y python3-pip curl && \
    pip3 install patroni[etcd] && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY patroni.yml /etc/patroni/patroni.yml

CMD ["patroni", "/etc/patroni/patroni.yml"]
```

---

## 📄 2. `pg-node/patroni.yml`

```yaml
# pg-node/patroni.yml
scope: payment_cluster
namespace: /db/
name: "{{ PATRONI_NAME }}"

restapi:
  listen: 0.0.0.0:8008
  connect_address: "{{ PATRONI_RESTAPI_CONNECT_ADDRESS }}"

etcd:
  host: etcd:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
    postgresql:
      use_pg_rewind: true
      use_slots: true
      parameters:
        wal_level: replica
        hot_standby: "on"
        max_wal_senders: 10
        wal_keep_size: 128MB
        max_replication_slots: 10
        logging_collector: off

postgresql:
  listen: 0.0.0.0:5432
  connect_address: "{{ PATRONI_POSTGRESQL_CONNECT_ADDRESS }}"
  data_dir: /var/lib/postgresql/data/pgdata
  bin_dir: /usr/lib/postgresql/16/bin
  authentication:
    replication:
      username: replicator
      password: repPass123
    superuser:
      username: postgres
      password: mysecretpassword
  parameters:
    shared_preload_libraries: pg_stat_statements
```

---

## 📄 3. `haproxy/haproxy.cfg`

```cfg
global
    maxconn 1000
    log stdout format raw local0

defaults
    log global
    mode tcp
    timeout connect 5s
    timeout client 30s
    timeout server 30s
    option tcp-check

# --- Запись: только мастер ---
frontend write_frontend
    bind *:5432
    default_backend write_backend

backend write_backend
    option pgsql-check user postgres
    server pg-node-1 pg-node-1:5432 check
    server pg-node-2 pg-node-2:5432 check backup

# --- Чтение: реплика → мастер ---
frontend read_frontend
    bind *:5433
    default_backend read_backend

backend read_backend
    option pgsql-check user postgres
    server pg-node-2 pg-node-2:5432 check
    server pg-node-1 pg-node-1:5432 check backup
```

---

## 📄 4. `initdb/01_extensions.sql` (пример)

```sql
-- initdb/01_extensions.sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

> Остальные SQL-файлы (`02_accounts_schema.sql`, `03_functions.sql`) — вставь свои DDL и функции.

---

## 📄 5. Обновлённый `docker-compose.yml`

```yaml
version: '3.8'

services:
  etcd:
    image: bitnami/etcd:latest
    environment:
      - ALLOW_NONE_AUTHENTICATION=yes
      - ETCD_ADVERTISE_CLIENT_URLS=http://etcd:2379
    networks:
      - backend

  pg-node-1:
    build: ./pg-node
    environment:
      PATRONI_NAME: pg-node-1
      PATRONI_RESTAPI_CONNECT_ADDRESS: pg-node-1:8008
      PATRONI_POSTGRESQL_CONNECT_ADDRESS: pg-node-1:5432
    volumes:
      - pgdata1:/var/lib/postgresql/data
    networks:
      - backend
    depends_on:
      - etcd

  pg-node-2:
    build: ./pg-node
    environment:
      PATRONI_NAME: pg-node-2
      PATRONI_RESTAPI_CONNECT_ADDRESS: pg-node-2:8008
      PATRONI_POSTGRESQL_CONNECT_ADDRESS: pg-node-2:5432
    volumes:
      - pgdata2:/var/lib/postgresql/data
    networks:
      - backend
    depends_on:
      - etcd

  haproxy:
    image: haproxytech/haproxy-alpine
    ports:
      - "5432:5432"  # write
      - "5433:5433"  # read
    volumes:
      - ./haproxy/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg
    networks:
      - backend
    depends_on:
      - pg-node-1
      - pg-node-2

  redis:
    image: redis:7-alpine
    networks: [backend]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  rabbitmq:
    image: rabbitmq:3.13-management
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    ports: ["5672:5672", "15672:15672"]
    networks: [backend]

  auth:
    build: ./auth
    ports: ["8001:8001"]
    environment:
      POSTGRES_HOST: haproxy
      POSTGRES_PORT: "5432"
      POSTGRES_DB: postgres
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: mysecretpassword
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET_KEY: my_secret_code
    depends_on:
      haproxy:
        condition: service_started
      redis:
        condition: service_healthy
    networks: [backend]

  users:
    build: ./users
    ports: ["8002:8002"]
    depends_on:
      haproxy:
        condition: service_started
    networks: [backend]

  webhook:
    build: ./webhook_2can
    ports: ["8000:8000"]
    depends_on:
      haproxy:
        condition: service_started
    networks: [backend]

volumes:
  pgdata1:
  pgdata2:

networks:
  backend:
    driver: bridge
```

---

## 📄 6. `users/.env`

```env
database_write_url=postgresql://postgres:mysecretpassword@haproxy:5432/postgres
database_read_url=postgresql://postgres:mysecretpassword@haproxy:5433/postgres
rabbitmq_url=amqp://guest:guest@rabbitmq:5672/
REDIS_URL=redis://redis:6379/1
log_dir=./logs
```

---

## 📄 7. `users/src/settings.py`

```python
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, PostgresDsn, RedisDsn, Field
from pathlib import Path
from typing import Set

class Settings(BaseSettings):
    database_write_url: PostgresDsn
    database_read_url: PostgresDsn
    rabbitmq_url: str
    redis_url: RedisDsn = Field(default="redis://redis:6379/1", alias="REDIS_URL")
    log_dir: Path = Path("./logs")
    MAX_UPLOAD_FILE_SIZE: int = Field(10 * 1024 * 1024, description="10 MB")
    ALLOWED_UPLOAD_EXTENSIONS: Set[str] = {".csv", ".xlsx", ".xls"}

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

settings = Settings()
```

---

## 📄 8. `users/src/db/pools.py`

```python
# users/src/db/pools.py
from asyncpg import create_pool, Pool
from src.settings import settings

write_pool: Pool
read_pool: Pool

async def init_pools():
    global write_pool, read_pool
    write_pool = await create_pool(str(settings.database_write_url))
    read_pool = await create_pool(str(settings.database_read_url))

async def close_pools():
    await write_pool.close()
    await read_pool.close()

# Зависимости для роутов
def get_write_pool() -> Pool:
    return write_pool

def get_read_pool() -> Pool:
    return read_pool
```

---

## 📄 9. `users/src/main.py`

```python
# users/src/main.py
from fastapi import FastAPI
from src.routers.accounts import router as accounts_router
from src.db.pools import init_pools, close_pools
from src.core.exceptions import setup_exception_handlers  # если есть

app = FastAPI(title="Users Service")

@app.on_event("startup")
async def startup():
    await init_pools()

@app.on_event("shutdown")
async def shutdown():
    await close_pools()

app.include_router(accounts_router, prefix="/accounts")
setup_exception_handlers(app)  # если используется
```

---

## 📄 10. Обнови зависимости в `users/requirements.txt`

```txt
asyncpg
fastapi
uvicorn
pydantic-settings
loguru
aioredis
# ... остальные
```

> `patroni` не нужен в `users` — только в `pg-node`.

---

## ▶️ Как запустить

1. Собери и запусти:
   ```bash
   docker-compose up --build
   ```
2. Убедись, что кластер инициализирован (мастер: `pg-node-1`).
3. Выполни инициализацию схем **один раз**:
   ```bash
   cat initdb/*.sql | docker exec -i $(docker-compose ps -q pg-node-1) psql -U postgres
   ```
4. Запусти тестовый запрос:
   ```bash
   curl "http://localhost:8002/accounts/users/by-identifier?identifier=+79991234567"
   ```

---

## ✅ Поведение при отказах

| Сценарий | Что происходит |
|--------|----------------|
| Реплика (`pg-node-2`) упала | Чтение идёт на `pg-node-1` (backup в HAProxy) |
| Мастер (`pg-node-1`) упал | Через ~30 сек Patroni делает `pg-node-2` мастером. HAProxy продолжает работать. |
| Бывший мастер восстановлен | Становится репликой автоматически. |

---
