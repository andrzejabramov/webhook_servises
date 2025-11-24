CREATE OR REPLACE FUNCTION "accounts"."update_user_profile"("p_id" uuid, "p_is_active" bool=NULL::boolean, "p_profile" jsonb=NULL::jsonb)
  RETURNS "accounts"."users" AS $BODY$
DECLARE
    updated_user accounts.users;
BEGIN
    UPDATE accounts.users
    SET
        profile = COALESCE(p_profile, profile),
        is_active = COALESCE(p_is_active, is_active),
        updated_at = now()
    WHERE id = p_id
    RETURNING * INTO updated_user;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'User % not found', p_id;
    END IF;

    RETURN updated_user;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100