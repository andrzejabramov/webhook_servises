CREATE OR REPLACE FUNCTION "accounts"."get_all_contact_types"()
  RETURNS SETOF "accounts"."contact_types" AS $BODY$
    SELECT * FROM "accounts"."contact_types" ORDER BY id;
$BODY$
  LANGUAGE sql STABLE
  COST 100
  ROWS 1000