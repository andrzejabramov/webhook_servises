CREATE OR REPLACE FUNCTION "accounts"."get_user_by_id"("p_id" uuid)
  RETURNS "accounts"."users" AS $BODY$
DECLARE
    user_rec accounts.users;
BEGIN
    SELECT * INTO user_rec FROM accounts.users WHERE id = p_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'User % not found', p_id;
    END IF;
    RETURN user_rec;
END;
$BODY$
  LANGUAGE plpgsql STABLE
  COST 100