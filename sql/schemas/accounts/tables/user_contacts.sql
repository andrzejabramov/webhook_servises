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

CREATE UNIQUE INDEX "idx_user_contacts_active_value_type" ON "accounts"."user_contacts" USING btree (
  "contact_type_id" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "value" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
) WHERE is_active = true;

CREATE TRIGGER "trg_user_contacts_updated_at" BEFORE UPDATE ON "accounts"."user_contacts"
FOR EACH ROW
EXECUTE PROCEDURE "accounts"."update_updated_at_column"();