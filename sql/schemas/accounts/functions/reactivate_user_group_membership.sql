CREATE OR REPLACE FUNCTION "accounts"."reactivate_user_group_membership"("p_user_id" uuid, "p_group_id" int2)
  RETURNS "accounts"."user_group_memberships" AS $BODY$
DECLARE
    updated_record "accounts"."user_group_memberships";
BEGIN
    UPDATE "accounts"."user_group_memberships"
    SET "is_active" = true,
        "deactivated_at" = NULL
    WHERE "user_id" = p_user_id
      AND "group_id" = p_group_id
    RETURNING * INTO updated_record;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Membership not found for user % in group %', p_user_id, p_group_id;
    END IF;

    RETURN updated_record;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100