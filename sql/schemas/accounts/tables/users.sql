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