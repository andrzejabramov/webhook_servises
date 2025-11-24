CREATE OR REPLACE FUNCTION "accounts"."remove_user_from_group"("p_user_id" uuid, "p_group_id" int2)
  RETURNS "accounts"."user_group_memberships" AS $BODY$
DECLARE
    updated_membership accounts.user_group_memberships;
BEGIN
    UPDATE accounts.user_group_memberships
    SET is_active = false, deactivated_at = now()
    WHERE user_id = p_user_id AND group_id = p_group_id AND is_active = true
    RETURNING * INTO updated_membership;

    RETURN updated_membership;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100