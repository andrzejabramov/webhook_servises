CREATE OR REPLACE FUNCTION "auth"."consume_refresh_token"("p_token_hash" text)
  RETURNS "pg_catalog"."uuid" AS $BODY$
DECLARE
    v_user_id UUID;
		v_expires_at TIMESTAMPTZ;
    v_revoked BOOLEAN;
BEGIN
    SELECT user_id, expires_at, revoked
    INTO v_user_id, v_expires_at, v_revoked
    FROM auth.refresh_tokens
    WHERE token_hash = p_token_hash;

    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    -- Проверяем: не отозван ли и не просрочен ли
    IF v_revoked OR v_expires_at <= NOW() THEN
        RETURN NULL;
    END IF;

    -- Отзываем токен: помечаем как revoked = true
    UPDATE auth.refresh_tokens
    SET revoked = true
    WHERE token_hash = p_token_hash;

    RETURN v_user_id;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100