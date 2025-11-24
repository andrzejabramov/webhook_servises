CREATE OR REPLACE FUNCTION "accounts"."update_user"("p_id" uuid, "p_username" text=NULL::text, "p_full_name" text=NULL::text, "p_profile" jsonb=NULL::jsonb, "p_is_active" bool=NULL::boolean)
  RETURNS "accounts"."users" AS $BODY$
DECLARE
    updated_user accounts.users;
BEGIN
    UPDATE accounts.users
    SET
        username = COALESCE(p_username, username),
        full_name = COALESCE(p_full_name, full_name),
        profile = COALESCE(p_profile, profile),
        is_active = COALESCE(p_is_active, is_active),
        updated_at = now()
    WHERE id = p_id
    RETURNING * INTO updated_user;

    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    RETURN updated_user;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100