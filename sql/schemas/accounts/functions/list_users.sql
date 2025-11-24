CREATE OR REPLACE FUNCTION "accounts"."list_users"()
  RETURNS SETOF "accounts"."users" AS $BODY$
    SELECT * FROM accounts.users ORDER BY created_at DESC;
$BODY$
  LANGUAGE sql STABLE
  COST 100
  ROWS 1000