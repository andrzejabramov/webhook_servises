CREATE OR REPLACE FUNCTION "accounts"."list_user_groups"()
  RETURNS SETOF "accounts"."user_groups" AS $BODY$
BEGIN
    RETURN QUERY
    SELECT * FROM accounts.user_groups
    ORDER BY id;
END;
$BODY$
  LANGUAGE plpgsql STABLE
  COST 100
  ROWS 1000