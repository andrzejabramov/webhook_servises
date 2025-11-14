
#
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


### 2. Управление группами → mydb

```commandline
POST /accounts/user-groups 
  → schemas.UserGroupCreate 
  → UserGroupService.create() 
  → PostgreSQL: accounts.create_user_group(name, description)
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

### Как добавить новый функционал без нарушения ядра?

| Фича                 | Где добавить                          | Не затрагивает            |
|----------------------|---------------------------------------|---------------------------|
| Авторизация          | `dependencies/auth.py` + `Depends()`   | `services/`, `db/`        |
| Кэширование          | `services/cache.py` + Redis-пул       | Роуты, схемы              |
| RabbitMQ-публикация  | `queue/publisher.py`                  | БД, настройки             |
| Аудит действий       | Новый сервис + таблица в `mydb`       | Вебхук, legacy            |

Принцип: новый функционал — новый модуль, старый код остаётся неизменным. 


### ✅ Следующие шаги (опционально)

1. Реализовать accounts.get_user_group(id) и другие функции в PostgreSQL.  
2. Добавить валидацию name (min/max length, regex).  
3. Подключить RABBITMQ_URL для публикации событий.  
4. Добавить middleware для логирования запросов.  


