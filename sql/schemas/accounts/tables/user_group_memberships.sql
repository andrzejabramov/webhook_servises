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