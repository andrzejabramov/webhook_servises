CREATE TABLE "to_can"."syspay" (
  "id" int4 NOT NULL DEFAULT nextval('"to_can".syspay_id_seq'::regclass),
  "json_inside" jsonb,
  "id_uuid" uuid NOT NULL,
  CONSTRAINT "syspay_copy1_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "id_uuid" UNIQUE ("id_uuid")
)
;