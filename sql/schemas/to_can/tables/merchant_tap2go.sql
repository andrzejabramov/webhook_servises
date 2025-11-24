CREATE TABLE "to_can"."merchant_tap2go" (
  "idmerch" int2 NOT NULL DEFAULT nextval('"to_can".merch_idmerch_seq'::regclass),
  "accesuaries" jsonb NOT NULL,
  "mid" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "syspay_merch" int4 NOT NULL,
  CONSTRAINT "merchant_tap2go_pkey" PRIMARY KEY ("idmerch"),
  CONSTRAINT "mid" UNIQUE ("mid"),
  CONSTRAINT "access" UNIQUE ("accesuaries")
)
;