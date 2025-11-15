# db.auth 

## tables

### refresh_tokens 
```commandline
CREATE TABLE "auth"."refresh_tokens" (
  "token_hash" text COLLATE "pg_catalog"."default" NOT NULL,
  "user_id" uuid NOT NULL,
  "created_at" timestamptz(6) DEFAULT now(),
  "expires_at" timestamptz(6) NOT NULL,
  "used" bool DEFAULT false,
  "revoked" bool DEFAULT false,
  CONSTRAINT "refresh_tokens_pkey" PRIMARY KEY ("token_hash")
)
;

ALTER TABLE "auth"."refresh_tokens" 
  OWNER TO "xxxxxxxx";

CREATE INDEX "idx_refresh_tokens_expires" ON "auth"."refresh_tokens" USING btree (
  "expires_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
) WHERE NOT revoked AND NOT used;

CREATE INDEX "idx_refresh_tokens_user_id" ON "auth"."refresh_tokens" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
```

## functions

### "consume_refresh_token"("p_token_hash" text) 
```commandline
CREATE OR REPLACE FUNCTION "auth"."consume_refresh_token"("p_token_hash" text)
  RETURNS "pg_catalog"."uuid" AS $BODY$
DECLARE
    v_user_id UUID;
BEGIN
    UPDATE auth.refresh_tokens
    SET used = TRUE
    WHERE token_hash = p_token_hash
      AND used = FALSE
      AND revoked = FALSE
      AND expires_at > NOW()
    RETURNING user_id INTO v_user_id;

    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'Invalid or expired refresh token';
    END IF;

    RETURN v_user_id;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
```

### "create_refresh_token"("p_user_id" uuid, "p_token_hash" text, "p_expires_at" timestamptz) 
```commandline
CREATE OR REPLACE FUNCTION "auth"."create_refresh_token"("p_user_id" uuid, "p_token_hash" text, "p_expires_at" timestamptz)
  RETURNS "pg_catalog"."void" AS $BODY$
BEGIN
    INSERT INTO auth.refresh_tokens (token_hash, user_id, expires_at)
    VALUES (p_token_hash, p_user_id, p_expires_at);
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
```

### "get_credential_by_login"("p_login" text, "p_type" text)
```commandline
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
```
