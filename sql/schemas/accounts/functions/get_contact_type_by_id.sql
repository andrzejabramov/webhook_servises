CREATE OR REPLACE FUNCTION "accounts"."get_contact_type_by_id"("p_id" int4)
  RETURNS "accounts"."contact_types" AS $BODY$
DECLARE
    rec "accounts"."contact_types";
BEGIN
    SELECT * INTO rec
    FROM "accounts"."contact_types"
    WHERE "id" = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Contact type % not found', p_id;
    END IF;

    RETURN rec;
END;
$BODY$
  LANGUAGE plpgsql STABLE
  COST 100