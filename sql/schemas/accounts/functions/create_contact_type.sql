CREATE OR REPLACE FUNCTION "accounts"."create_contact_type"("p_name" text)
  RETURNS "accounts"."contact_types" AS $BODY$
DECLARE
    rec "accounts"."contact_types";
BEGIN
    INSERT INTO "accounts"."contact_types" ("name")
    VALUES (p_name)
    RETURNING * INTO rec;
    RETURN rec;
EXCEPTION WHEN unique_violation THEN
    RAISE EXCEPTION 'Contact type "%" already exists', p_name;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100