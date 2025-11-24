CREATE OR REPLACE FUNCTION "accounts"."create_user_group_membership"("p_user_id" uuid, "p_group_id" int2)
  RETURNS "accounts"."user_group_memberships" AS $BODY$
DECLARE
    new_record "accounts"."user_group_memberships";
BEGIN
    -- Вставляем только если такой связи ещё нет (даже неактивной)
    INSERT INTO "accounts"."user_group_memberships" (
        "user_id",
        "group_id",
        "is_active",
        "deactivated_at"
    )
    VALUES (
        p_user_id,
        p_group_id,
        true,
        NULL
    )
    ON CONFLICT ("user_id", "group_id") DO UPDATE
        SET "is_active" = true,
            "deactivated_at" = NULL
    RETURNING * INTO new_record;

    RETURN new_record;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100