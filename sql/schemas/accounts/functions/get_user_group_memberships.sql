CREATE OR REPLACE FUNCTION "accounts"."get_user_group_membership"("p_user_id" uuid, "p_group_id" int2)
  RETURNS "accounts"."user_group_memberships" AS $BODY$
DECLARE
    result_record "accounts"."user_group_memberships";
BEGIN
    SELECT * INTO result_record
    FROM "accounts"."user_group_memberships"
    WHERE "user_id" = p_user_id
      AND "group_id" = p_group_id;

    IF NOT FOUND THEN
        RETURN NULL;  -- или RAISE EXCEPTION, если предпочитаешь
    END IF;

    RETURN result_record;
END;
$BODY$
  LANGUAGE plpgsql STABLE
  COST 100;