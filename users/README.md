set -e

# Создаём корень проекта
mkdir -p webhook-platform/{services/webhook-receiver/src/{db,dependencies,schemas},services/consumer-analytics,services/consumer-billing}

cd webhook-platform

# .gitignore
cat > .gitignore << 'EOF'
.venv/
*/.venv/
.env
__pycache__/
*.pyc
*.log
logs/
EOF

# .env.example
cat > .env.example << 'EOF'
POSTGRES_DB=executor
POSTGRES_USER=paydb
POSTGRES_PASSWORD=Moresun@98

RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest

DATABASE_URL=postgresql://paydb:Moresun%4098@postgres:5432/executor
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

ANALYTICS_API_URL=https://analytics.example.com/webhook
BILLING_API_URL=https://billing.example.com/events
EOF

# README.md
cat > README.md << 'EOF'
# Webhook Platform

Монорепозиторий с микросервисами:
- `webhook-receiver` — принимает вебхуки, пишет в PostgreSQL, публикует в RabbitMQ
- `consumer-analytics` — читает из очереди и отправляет в аналитику
- `consumer-billing` — читает из очереди и отправляет в биллинг

## Запуск

```bash
cp .env.example .env          # заполните секреты
set -e

# Создаём корень проекта
mkdir -p webhook-platform/{services/webhook-receiver/src/{db,dependencies,schemas},services/consumer-analytics,services/consumer-billing}

cd webhook-platform

# .gitignore
cat > .gitignore << 'EOF'
.venv/
*/.venv/
.env
__pycache__/
*.pyc
*.log
logs/
EOF

# .env.example
cat > .env.example << 'EOF'
POSTGRES_DB=executor
POSTGRES_USER=paydb
POSTGRES_PASSWORD=Moresun@98

RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest

DATABASE_URL=postgresql://paydb:Moresun%4098@postgres:5432/executor
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

ANALYTICS_API_URL=https://analytics.example.com/webhook
BILLING_API_URL=https://billing.example.com/events
EOF

# README.md
cat > README.md << 'EOF'
# Webhook Platform

Монорепозиторий с микросервисами:
- `webhook-receiver` — принимает вебхуки, пишет в PostgreSQL, публикует в RabbitMQ
- `consumer-analytics` — читает из очереди и отправляет в аналитику
- `consumer-billing` — читает из очереди и отправляет в биллинг

## Запуск

```bash
cp .env.example .env    set -e

# Создаём корень проекта
mkdir -p webhook-platform/{services/webhook-receiver/src/{db,dependencies,schemas},services/consumer-analytics,services/consumer-billing}

cd webhook-platform

# .gitignore
cat > .gitignore << 'EOF'
.venv/
*/.venv/
.env
__pycache__/
*.pyc
*.log
logs/
EOF

# .env.example
cat > .env.example << 'EOF'
POSTGRES_DB=executor
POSTGRES_USER=paydb
POSTGRES_PASSWORD=Moresun@98

RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest

DATABASE_URL=postgresql://paydb:Moresun%4098@postgres:5432/executor
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

ANALYTICS_API_URL=https://analytics.example.com/webhook
BILLING_API_URL=https://billing.example.com/events
EOF

# README.md
cat > README.md << 'EOF'
# Webhook Platform

Монорепозиторий с микросервисами:
- `webhook-receiver` — принимает вебхуки, пишет в PostgreSQL, публикует в RabbitMQ
- `consumer-analytics` — читает из очереди и отправляет в аналитику
- `consumer-billing` — читает из очереди и отправляет в биллинг

## Запуск

```bash
cp .env.example .env          # заполните секреты
      # заполните секреты
docker-compose up --build   
EOF
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
postgres:
image: postgres:15
environment:
POSTGRES_DB: POSTGRES 
D
​
 BPOSTGRES 
U
​
 SER: {POSTGRES_USER}
POSTGRES_PASSWORD: POSTGRES 
P
​
 ASSWORDports:−"5432:5432"volumes:−postgres 
/
​
 var/lib/postgresql/datahealthcheck:test:["CMD−SHELL","pg 
i
​
 sready−U {POSTGRES_USER} -d ${POSTGRES_DB}"]
interval: 5s
timeout: 5s
retries: 5

rabbitmq:
image: rabbitmq:3-management
ports:
- "5672:5672"
- "15672:15672"
environment:
RABBITMQ_DEFAULT_USER: RABBITMQ 
D
​
 EFAULT 
U
​
 SERRABBITMQ 
D
​
 EFAULT 
P
​
 ASS: {RABBITMQ_DEFAULT_PASS}
healthcheck:
test: ["CMD", "rabbitmq-diagnostics", "ping"]
interval: 5s
timeout: 5s
retries: 5

webhook-receiver:
build: ./services/webhook-receiver
ports:
- "8000:8000"
environment:
DATABASE_URL: DATABASE 
U
​
 RLRABBITMQ 
U
​
 RL: {RABBITMQ_URL}
depends_on:
postgres:
condition: service_healthy
rabbitmq:
condition: service_healthy

consumer-analytics:
build: ./services/consumer-analytics
environment:
RABBITMQ_URL: RABBITMQ 
U
​
 RLTARGET 
A
​
 PI 
U
​
 RL: {ANALYTICS_API_URL}
depends_on:
rabbitmq:
condition: service_healthy

consumer-billing:
build: ./services/consumer-billing
environment:
RABBITMQ_URL: RABBITMQ 
U
​
 RLTARGET 
A
​
 PI 
U
​
 RL: {BILLING_API_URL}
depends_on:
rabbitmq:
condition: service_healthy

volumes:
postgres_
EOF

cd services/webhook-receiver

cat > requirements.txt << 'EOF'
fastapi
uvicorn[standard]
asyncpg
aio-pika
pydantic-settings
loguru
EOF

cat > Dockerfile << 'EOF'
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

mkdir -p src/db src/dependencies src/schemas
touch src/init.py src/db/init.py src/dependencies/init.py src/schemas/init.py

cat > src/settings.py << 'EOF'
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
database_url: str
rabbitmq_url: str
log_dir: Path = Path("./logs")

class Config:
env_file = ".env"
settings = Settings()
EOF

cat > src/main.py << 'EOF'
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.db.pools import init_main_db_pool, close_main_db_pool
from src.routers import webhook

@asynccontextmanager
async def lifespan(app: FastAPI):
await init_main_db_pool()
yield
await close_main_db_pool()

app = FastAPI(lifespan=lifespan)
app.include_router(webhook.router, prefix="/webhook")
EOF

cd ../consumer-analytics

cat > requirements.txt << 'EOF'
aio-pika
httpx
loguru
EOF

cat > Dockerfile << 'EOF'
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
EOF

cat > main.py << 'EOF'
import asyncio
import os
import json
import httpx
from loguru import logger
import aio_pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
TARGET_API_URL = os.getenv("TARGET_API_URL")

async def process_message(message: aio_pika.IncomingMessage):
async with message.process():
try:
data = json.loads(message.body)
logger.info(f"Sending to analytics: {data}")
async with httpx.AsyncClient() as client:
await client.post(TARGET_API_URL, json=data)
except Exception as e:
logger.error(f"Failed to send: {e}")

async def main():
connection = await aio_pika.connect_robust(RABBITMQ_URL)
channel = await connection.channel()
await channel.set_qos(prefetch_count=1)

exchange = await channel.declare_exchange("webhook.processed", aio_pika.ExchangeType.FANOUT)
queue = await channel.declare_queue("analytics_queue", durable=True)
await queue.bind(exchange)

await queue.consume(process_message)
logger.info("Analytics consumer started")
try:
await asyncio.Future()
finally:
await connection.close()
if name == "main":
logger.remove()
logger.add(lambda msg: print(msg, end=""))
asyncio.run(main())
EOF

cd ../consumer-billing
cp ../consumer-analytics/requirements.txt .
cp ../consumer-analytics/Dockerfile .
cp ../consumer-analytics/main.py .

cd ../..
echo "✅ Структура проекта создана в папке webhook-platform"
echo "👉 Выполните: cd webhook-platform && cp .env.example .env"

