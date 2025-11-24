CREATE OR REPLACE FUNCTION "accounts"."create_user"("p_profile" jsonb=NULL::jsonb)
  RETURNS "accounts"."users" AS $BODY$
DECLARE
    new_user accounts.users;
BEGIN
    INSERT INTO accounts.users (profile)
    VALUES (p_profile)
    RETURNING * INTO new_user;
    RETURN new_user;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'User with username "%" already exists', p_username;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100