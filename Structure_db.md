## 🗃 Структура баз данных PostgreSQL

postgresql/  
├── main/                                 # Основная база данных (для запросов на запись и изменение)  
│   ├── accounts/  
│   │   ├── Tables:  
│   │   │   ├── users  
│   │   │   ├── user_groups  
│   │   │   ├── user_group_memberships       -- M2M  
│   │   │   ├── contact_types  
│   │   │   └── user_contacts                -- M2M  
│   │   └── Functions:  
│   │       ├── add_user_to_group(p_user_id uuid, p_group_id int2)  
│   │       ├── create_contact_type(p_name text)  
│   │       ├── create_user(p_contact_email text=NULL, p_username text=NULL, p_profile jsonb=NULL)  
│   │       ├── create_user(p_username text, p_profile jsonb=NULL)  -- перегрузка  
│   │       ├── create_user_contact(p_user_id uuid, p_contact_type_id int4, p_value text)  
│   │       ├── create_user_group(p_name text, p_description text=NULL)  
│   │       ├── create_user_group_membership(p_user_id uuid, p_group_id int2)  
│   │       ├── deactivate_user(p_id uuid)  
│   │       ├── deactivate_user_contact(p_id uuid)  
│   │       ├── deactivate_user_group_membership(p_user_id uuid, p_group_id int2)  
│   │       ├── get_all_contact_types()  
│   │       ├── get_contact_type_by_id(p_id int4)  
│   │       ├── get_user_by_id(p_id uuid)  
│   │       ├── get_user_contact_by_id(p_id uuid)  
│   │       ├── get_user_contacts_by_user_id(p_user_id uuid, p_only_active bool=true)    
│   │       ├── get_user_group_membership(p_user_id uuid, p_group_id int2)  
│   │       ├── get_user_groups(p_user_id uuid)  
│   │       ├── get_user_groups(p_user_id uuid, p_only_active bool=true)  -- перегрузка  
│   │       ├── list_contact_types()  
│   │       ├── list_user_groups()  
│   │       ├── list_users()  
│   │       ├── reactivate_user(p_id uuid)  
│   │       ├── reactivate_user_contact(p_id uuid)  
│   │       ├── reactivate_user_group_membership(p_user_id uuid, p_group_id int2)  
│   │       ├── remove_user_from_group(p_user_id uuid, p_group_id int2)  
│   │       ├── set_updated_at()  
│   │       ├── update_updated_at_column()  
│   │       ├── update_user(p_id uuid, p_username text=NULL, p_full_name text=NULL, p_profile jsonb=NULL, p_is_active bool=NULL)  
│   │       ├── update_user_group(p_id int2, p_name text=NULL, p_description text=NULL, p_is_active bool=NULL)  
│   │       └── update_user_profile(p_id uuid, p_is_active bool=NULL, p_profile jsonb=NULL)    
│   │  
│   ├── auth/  
│   │   ├── Tables:  
│   │   │   └── refresh_tokens  
│   │   └── Functions:  
│   │       ├── consume_refresh_token(p_token_hash text)  
│   │       ├── get_credential_by_login(p_login text, p_type text)  
│   │       └── create_refresh_token(p_user_id uuid, p_token_hash text, p_expires_at timestamptz)  
│   │  
│   └── to_can/    
│       ├── Tables:  
│       │   ├── merchant_tap2go  
│       │   └── syspay  
│       └── Functions:  
│           ├── f_syspay(x_json json)  
│           ├── f_payment(x_ins jsonb)  
│           └── f_tr_payment()  
│  
└── replica/                              # Реплика базы данных (только для запросов на чтение)  
    ├── accounts/                         # Идентичная структура: таблицы и функции только для чтения  
    │   ├── Tables:                       # -- те же таблицы (только SELECT)  
    │   └── Functions:                    # -- только функции без побочных эффектов (например: get_*, list_*)  
    │  
    ├── auth/  
    │   ├── Tables:  
    │   │   └── refresh_tokens            # (часто не реплицируется, но если реплицируется — только для чтения)  
    │   └── Functions:  
    │       └── get_credential_by_login(p_login text, p_type text)  -- допустима на реплике  
    │  
    └── to_can/  
        ├── Tables:  
        │   ├── merchant_tap2go  
        │   └── syspay  
        └── Functions:  
            ├── f_syspay(x_json json)     # зависит от логики — если только чтение, может быть на реплике  
            ├── f_payment(x_ins jsonb)    # обычно только на main  
            └── f_tr_payment()            # обычно только на main  

## 📝 Пояснение
- main — используется микросервисами (auth, users, webhook_2can) для выполнения всех изменяющих операций (INSERT/UPDATE/DELETE) и вызова соответствующих CRUD-функций.  
- replica — предназначена исключительно для чтения; на неё направляются запросы типа:  
- get_*  
- list_*  
- get_user_*  
- и другие функции без побочных эффектов.  
Некоторые функции вроде f_payment, f_tr_payment, create_*, update_*, deactivate_* не должны вызываться на реплике — они работают только в main.  
Функции триггеров (set_updated_at, update_updated_at_column) используются внутри БД и не вызываются напрямую из Python, но включены в схему для полноты.  
Схема to_can частично может содержать только чтение-ориентированные функции на реплике — это зависит от бизнес-логики.  
