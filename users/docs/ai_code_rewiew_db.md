# postgers_db

## tables

### contact_types
```commandline
CREATE TABLE "accounts"."contact_types" (
  "id" int4 NOT NULL DEFAULT nextval('"accounts".contacts_id_seq'::regclass),
  "name" text COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamptz(6) DEFAULT now(),
  CONSTRAINT "contacts_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "contacts_name_key" UNIQUE ("name")
)
;

ALTER TABLE "accounts"."contact_types" 
  OWNER TO "xxxxxxxxx";
```

### user_contacts
```commandline
CREATE TABLE "accounts"."user_contacts" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "user_id" uuid NOT NULL,
  "contact_type_id" int4 NOT NULL,
  "value" text COLLATE "pg_catalog"."default" NOT NULL,
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) DEFAULT now(),
  "updated_at" timestamptz(6) DEFAULT now(),
  CONSTRAINT "user_contacts_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "fk_user_contacts_type" FOREIGN KEY ("contact_type_id") REFERENCES "accounts"."contact_types" ("id") ON DELETE RESTRICT ON UPDATE NO ACTION,
  CONSTRAINT "fk_user_contacts_user" FOREIGN KEY ("user_id") REFERENCES "accounts"."users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION
)
;

ALTER TABLE "accounts"."user_contacts" 
  OWNER TO "xxxxxxxxxx";

CREATE TRIGGER "trg_user_contacts_updated_at" BEFORE UPDATE ON "accounts"."user_contacts"
FOR EACH ROW
EXECUTE PROCEDURE "accounts"."update_updated_at_column"();
```

### user_group_memberships
```commandline
CREATE TABLE "accounts"."user_group_memberships" (
  "user_id" uuid NOT NULL,
  "group_id" int2 NOT NULL,
  "is_active" bool NOT NULL DEFAULT true,
  "deactivated_at" timestamptz(6),
  CONSTRAINT "user_group_memberships_pkey" PRIMARY KEY ("user_id", "group_id"),
  CONSTRAINT "user_group_memberships_group_id_fkey" FOREIGN KEY ("group_id") REFERENCES "accounts"."user_groups" ("id") ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT "user_group_memberships_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "accounts"."users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION
)
;

ALTER TABLE "accounts"."user_group_memberships" 
  OWNER TO "xxxxxxxxx";
```
### user_groups
```commandline
CREATE TABLE "accounts"."user_groups" (
  "id" int2 NOT NULL GENERATED ALWAYS AS IDENTITY (
INCREMENT 1
MINVALUE  1
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
)
;

ALTER TABLE "accounts"."user_groups" 
  OWNER TO "xxxxxxxxxxx";

CREATE TRIGGER "tr_user_groups_set_updated_at" BEFORE UPDATE ON "accounts"."user_groups"
FOR EACH ROW
EXECUTE PROCEDURE "accounts"."set_updated_at"();
```

### users
```commandline
CREATE TABLE "accounts"."users" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) DEFAULT now(),
  "updated_at" timestamptz(6) DEFAULT now(),
  "profile" jsonb,
  "password_hash" text COLLATE "pg_catalog"."default",
  "password_updated_at" timestamptz(0),
  CONSTRAINT "users_pkey" PRIMARY KEY ("id")
)
;

ALTER TABLE "accounts"."users" 
  OWNER TO "xxxxxxxxx";
```

