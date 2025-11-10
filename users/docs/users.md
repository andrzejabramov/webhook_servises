# Сущность: Users

## 🗂 База данных
- **БД**: `mydb`
- **Схема**: `accounts`
- **Основная таблица**: `users`
- **Вспомогательные таблицы**: `contacts`, `user_group_memberships`

## 📐 Таблица `accounts.users`

Хранит **основную идентичность пользователя**. Не содержит контактных данных — только технические и опциональные атрибуты.

```sql
CREATE TABLE accounts.users (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  username TEXT,
  full_name TEXT,
  profile JSONB,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT users_pkey PRIMARY KEY (id),
  CONSTRAINT users_username_key UNIQUE (username)
);
```
profile
Qwen3-Max
4:58 pm
Конечно! Вот готовый файл docs/db/users.md, полностью согласованный с твоей архитектурой и обсуждёнными решениями.

📄 docs/db/users.md
md


1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
# Сущность: Users

## 🗂 База данных
- **БД**: `mydb`
- **Схема**: `accounts`
- **Основная таблица**: `users`
- **Вспомогательные таблицы**: `contacts`, `user_group_memberships`

## 📐 Таблица `accounts.users`

Хранит **основную идентичность пользователя**. Не содержит контактных данных — только технические и опциональные атрибуты.

```sql
CREATE TABLE accounts.users (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  username TEXT,
  full_name TEXT,
  profile JSONB,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT users_pkey PRIMARY KEY (id),
  CONSTRAINT users_username_key UNIQUE (username)
);
```
### Поля

| Поле | Тип | Описание |
|------|-----|--------|
| `id` | `UUID` | Неизменяемый системный идентификатор (основной ключ) |
| `username` | `TEXT` | Дружественный логин, управляемый пользователем, уникален, может быть `NULL` |
| `full_name` | `TEXT` | Часто используемое поле — вынесено из `JSONB` |
| `profile` | `JSONB` | Редко используемые/гибкие атрибуты: возраст, пол, локация и т.д. |
| `is_active` | `BOOLEAN` | Флаг активности (удаление заменено на `is_active = false`) |
| `created_at` | `TIMESTAMPTZ` | Время создания записи (авто: `now()`) |
| `updated_at` | `TIMESTAMPTZ` | Время последнего обновления (авто: `now()`) |

## 📞 Таблица accounts.contacts (M:1 к users)   
Хранит контактные данные с поддержкой истории и нескольких каналов.  

```commandline
CREATE TYPE accounts.contact_type AS ENUM ('email', 'phone');

CREATE TABLE accounts.contacts (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES accounts.users(id) ON DELETE CASCADE,
  contact_type accounts.contact_type NOT NULL,
  value TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  deactivated_at TIMESTAMPTZ,
  CONSTRAINT contacts_pkey PRIMARY KEY (id)
);

-- Только один активный email и телефон на пользователя
CREATE UNIQUE INDEX contacts_active_email ON accounts.contacts (user_id)
WHERE contact_type = 'email' AND is_active = true;

CREATE UNIQUE INDEX contacts_active_phone ON accounts.contacts (user_id)
WHERE contact_type = 'phone' AND is_active = true;
```
| Поле | Тип | Описание |
|------|-----|--------|
| `id` | `UUID` | Уникальный идентификатор контакта |
| `user_id` | `UUID` | Ссылка на `accounts.users.id` (каскадное удаление) |
| `contact_type` | `contact_type` (ENUM) | Тип контакта: `'email'` или `'phone'` |
| `value` | `TEXT` | Значение контакта (email или номер телефона) |
| `is_active` | `BOOLEAN` | Активен ли контакт (`true`/`false`) |
| `created_at` | `TIMESTAMPTZ` | Время привязки контакта |
| `deactivated_at` | `TIMESTAMPTZ` | Время отвязки (если `is_active = false`) |


### Логика работы  
При смене контакта:   
Старая запись: is_active = false, deactivated_at = now()   
Новая запись: is_active = true   
Поддерживает несколько неактивных записей для аудита.   

## 👥 Таблица accounts.user_group_memberships (M:N)
Связывает пользователей и группы.

```commandline
CREATE TABLE accounts.user_group_memberships (
  user_id UUID NOT NULL REFERENCES accounts.users(id) ON DELETE CASCADE,
  group_id INT2 NOT NULL REFERENCES accounts.user_groups(id) ON DELETE CASCADE,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  deactivated_at TIMESTAMPTZ,
  CONSTRAINT user_group_memberships_pkey PRIMARY KEY (user_id, group_id)
);
```
| Поле | Тип | Описание |
|------|-----|--------|
| `user_id` | `UUID` | Ссылка на `accounts.users.id` |
| `group_id` | `INT2` | Ссылка на `accounts.user_groups.id` |
| `is_active` | `BOOLEAN` | Активно ли членство (`true`/`false`) |
| `created_at` | `TIMESTAMPTZ` | Время вступления в группу |
| `deactivated_at` | `TIMESTAMPTZ` | Время исключения из группы (если `is_active = false`) |

## 🔌 PostgreSQL-функции (запланированы)
create_user(username, full_name, profile) → возвращает полную запись  
update_user(id, ...) → частичное обновление с COALESCE  
add_contact(user_id, contact_type, value) → деактивирует старые контакты того же типа  
list_users() → все пользователи  
get_user(id) → полная запись + активные контакты (JOIN)  

## 🧾 Pydantic-схемы (пример)  

```commandline
class UserCreate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    profile: Optional[dict] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    profile: Optional[dict] = None
    is_active: Optional[bool] = None

class UserRead(UserCreate):
    id: UUID4
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
```

## 💡 Особенности архитектуры
Идентификация:
Основной — id UUID, резервный — username TEXT.  
Контакты:  
Отдельная таблица с историей, а не в users или profile.  
Масштабируемость:  
profile JSONB позволяет добавлять атрибуты без миграций.  
Безопасность:  
Непредсказуемый id защищает от enumeration-атак.  
Гибкость:  
Пользователь может потерять телефон — вход возможен по username или через восстановление контакта.  



