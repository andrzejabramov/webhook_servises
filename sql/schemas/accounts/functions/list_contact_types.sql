CREATE OR REPLACE FUNCTION "accounts"."list_contact_types"()
  RETURNS SETOF "accounts"."contact_types" AS $BODY$
BEGIN
    RETURN QUERY
    SELECT * FROM "accounts"."contact_types"
    ORDER BY "id";
END;
$BODY$
  LANGUAGE plpgsql STABLE
  COST 100
  ROWS 1000