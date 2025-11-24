CREATE OR REPLACE FUNCTION "accounts"."add_user_to_group"("p_user_id" uuid, "p_group_id" int2)
  RETURNS "accounts"."user_group_memberships" AS $BODY$
DECLARE
    membership accounts.user_group_memberships;
BEGIN
    -- Если запись уже есть — реактивируем
    UPDATE accounts.user_group_memberships
    SET is_active = true, deactivated_at = NULL, created_at = now()
    WHERE user_id = p_user_id AND group_id = p_group_id
    RETURNING * INTO membership;

    IF membership IS NULL THEN
        INSERT INTO accounts.user_group_memberships (user_id, group_id)
        VALUES (p_user_id, p_group_id)
        RETURNING * INTO membership;
    END IF;

    RETURN membership;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100