CREATE OR REPLACE FUNCTION "accounts"."reactivate_user"("p_id" uuid)
  RETURNS "accounts"."users" AS $BODY$
DECLARE
    reactivated_user accounts.users;
BEGIN
    UPDATE accounts.users
    SET is_active = true, updated_at = now()
    WHERE id = p_id
    RETURNING * INTO reactivated_user;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'User % not found', p_id;
    END IF;
    RETURN reactivated_user;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100