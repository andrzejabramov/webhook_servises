CREATE OR REPLACE FUNCTION "accounts"."create_user_group"("p_name" text, "p_description" text=NULL::text)
  RETURNS "accounts"."user_groups" AS $BODY$
DECLARE
    new_record accounts.user_groups;
BEGIN
    INSERT INTO accounts.user_groups (name, description)
    VALUES (p_name, p_description)
    RETURNING * INTO new_record;

    RETURN new_record;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'User group with name "%" already exists', p_name;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100