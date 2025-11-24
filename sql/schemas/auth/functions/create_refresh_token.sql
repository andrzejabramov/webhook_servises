CREATE OR REPLACE FUNCTION "auth"."create_refresh_token"("p_user_id" uuid, "p_token_hash" text, "p_expires_at" text)
  RETURNS "pg_catalog"."void" AS $BODY$
BEGIN
    INSERT INTO auth.refresh_tokens (token_hash, user_id, expires_at)
    VALUES (p_token_hash, p_user_id, p_expires_at);
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100