CREATE TABLE "accounts"."contact_types" (
  "id" int4 NOT NULL DEFAULT nextval('"accounts".contacts_id_seq'::regclass),
  "name" text COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamptz(6) DEFAULT now(),
  CONSTRAINT "contacts_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "contacts_name_key" UNIQUE ("name")
)
;