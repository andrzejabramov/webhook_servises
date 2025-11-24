CREATE OR REPLACE FUNCTION "accounts"."get_active_user_contact_by_value"("p_value" text)
  RETURNS TABLE("user_id" uuid, "password_hash" text) AS $BODY$
BEGIN
    RETURN QUERY
    SELECT
        u.id AS user_id,
        u.password_hash
    FROM accounts.user_contacts uc
    JOIN accounts.contact_types ct ON uc.contact_type_id = ct.id
    JOIN accounts.users u ON uc.user_id = u.id
    WHERE uc.value = p_value
      AND uc.is_active = TRUE
      AND ct.name = ANY(ARRAY['second_login', 'email', 'phone'])
      AND u.is_active = TRUE;  -- ← важно: не "status", а "is_active"
END;
$BODY$
  LANGUAGE plpgsql STABLE
  COST 100
  ROWS 1000