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

CREATE TRIGGER "tr_user_groups_set_updated_at" BEFORE UPDATE ON "accounts"."user_groups"
FOR EACH ROW
EXECUTE PROCEDURE "accounts"."set_updated_at"();