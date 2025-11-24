CREATE TABLE "auth"."refresh_tokens" (
  "token_hash" text COLLATE "pg_catalog"."default" NOT NULL,
  "user_id" uuid NOT NULL,
  "created_at" timestamptz(6) DEFAULT now(),
  "expires_at" timestamptz(6) NOT NULL,
  "revoked" bool DEFAULT false,
  CONSTRAINT "refresh_tokens_pkey" PRIMARY KEY ("token_hash")
)
;

CREATE INDEX "idx_refresh_tokens_expires" ON "auth"."refresh_tokens" USING btree (
  "expires_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
) WHERE NOT revoked;

CREATE INDEX "idx_refresh_tokens_user_id" ON "auth"."refresh_tokens" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST