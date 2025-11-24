CREATE OR REPLACE FUNCTION "accounts"."count_users"()
  RETURNS "pg_catalog"."int8" AS $BODY$
BEGIN
    RETURN (SELECT COUNT(*) FROM accounts.users);
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100