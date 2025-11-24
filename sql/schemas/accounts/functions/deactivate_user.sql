CREATE OR REPLACE FUNCTION "accounts"."deactivate_user"("p_id" uuid)
  RETURNS "accounts"."users" AS $BODY$
DECLARE
    deactivated_user accounts.users;
BEGIN
    UPDATE accounts.users
    SET is_active = false, updated_at = now()
    WHERE id = p_id
    RETURNING * INTO deactivated_user;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'User % not found', p_id;
    END IF;
    RETURN deactivated_user;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100