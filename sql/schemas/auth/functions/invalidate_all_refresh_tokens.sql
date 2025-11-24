CREATE OR REPLACE FUNCTION "auth"."invalidate_all_refresh_tokens"("p_user_id" uuid)
  RETURNS "pg_catalog"."void" AS $BODY$
BEGIN
    DELETE FROM auth.refresh_tokens
    WHERE user_id = p_user_id;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100