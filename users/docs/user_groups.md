# Таблица `user_groups`

## 🗂 Схема и БД
- **База данных**: `mydb` (новая БД, а не `paydb` — избегаем избыточности JSONB).
- **Схема**: `accounts`.
- **Владелец**: `andrzejvod`.

## 📐 Структура таблицы

```sql
CREATE TABLE "accounts"."user_groups" (
  "id" int2 NOT NULL GENERATED ALWAYS AS IDENTITY (
    INCREMENT 1
    MINVALUE 1
    MAXVALUE 32767
    START 1
  ),
  "name" text COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) DEFAULT now(),
  "updated_at" timestamptz(6) DEFAULT now(),
  CONSTRAINT "user_groups_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "user_groups_name_key" UNIQUE ("name")
);
```

## 🔐 Политики и договорённости
Удаление записей:
Запрещено. Вместо DELETE — обновление поля is_active = false.
Активность группы:
Поле is_active используется для моментального отключения доступа всей группы.
Идентификатор:
id — int2 с автоинкрементом (ожидается ≤ 10 групп → достаточно smallint).
Уникальность:
name — уникальный, регистрозависимый (по умолчанию).
⏱ Временные метки
created_at — фиксируется при INSERT, не изменяется.
updated_at — автоматически обновляется при любом UPDATE (кроме самих временных полей).
### Триггер для updated_at
```commandline
CREATE OR REPLACE FUNCTION accounts.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_user_groups_set_updated_at
BEFORE UPDATE ON accounts.user_groups
FOR EACH ROW
EXECUTE FUNCTION accounts.set_updated_at();
```

### 🔗 Связи
Связана с таблицей user_group_memberships (M2M: user_id ↔ group_id).
Внешний ключ: group_id → user_groups.id с ON DELETE CASCADE.
Системные триггеры (RI_FKey_*) — автоматические, не трогать.

### 📤 Взаимодействие с бэкендом
CRUD реализуется через хранимые функции PostgreSQL, а не через ORM.
Все функции:
Принимают один аргумент типа jsonb.
Возвращают результат в формате jsonb.
Выполняются из Python (FastAPI) через asyncpg.
### Пример сигнатуры:
```commandline
CREATE FUNCTION accounts.add_user_group(data jsonb) RETURNS jsonb AS $$ ... $$ LANGUAGE plpgsql;
```

### 🗃 Архитектурные принципы
JSONB используется только там, где действительно нужно (например, шаблоны для внешних сервисов).
В user_groups — только структурированные поля, без JSONB.
Унификация: один endpoint — любой объём данных (1 запись или CSV → 1000 записей).
Весь код — асинхронный (async/await, asyncpg).
### 🔜 Следующие шаги (на момент 2025-11-07)
Реализовать CRUD-функции для user_groups в схеме accounts:
add_user_group(jsonb) → jsonb
update_user_group(jsonb) → jsonb
get_user_group(id) → jsonb
(DELETE → обновление is_active)
Интегрировать в FastAPI-роут /accounts/groups.
