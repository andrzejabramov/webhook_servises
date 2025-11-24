CREATE OR REPLACE FUNCTION "auth"."get_credential_by_login"("p_login" text, "p_type" text)
  RETURNS TABLE("id" uuid, "user_id" uuid, "login" text, "credential_type" text, "password_hash" text, "is_primary" bool, "status" bool) AS $BODY$
BEGIN
    RETURN QUERY
    SELECT c.id, c.user_id, c.login, c.credential_type, c.password_hash, c.is_primary, c.status
    FROM auth.credentials c
    WHERE c.login = p_login
      AND c.credential_type = p_type
      AND c.status = TRUE;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000