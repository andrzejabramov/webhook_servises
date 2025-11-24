CREATE OR REPLACE FUNCTION "accounts"."get_user_by_identifier_v1"("identifier" text)
  RETURNS TABLE("id" uuid, "created_at" timestamptz, "updated_at" timestamptz, "is_active" bool, "profile" jsonb, "groups" json, "contacts" json) AS $BODY$
DECLARE
    v_is_uuid BOOLEAN := false;
    v_is_phone BOOLEAN := false;
    v_is_email BOOLEAN := false;
    v_user_id UUID;
BEGIN
    -- 1. Проверка: является ли identifier валидным UUID
    BEGIN
        v_user_id := identifier::UUID;
        v_is_uuid := true;
    EXCEPTION WHEN invalid_text_representation THEN
        v_is_uuid := false;
    END;

    -- 2. Если это UUID — ищем напрямую по users.id
    IF v_is_uuid THEN
        RETURN QUERY
        SELECT
            u.id,
            u.created_at,
            u.updated_at,
            u.is_active,
            u.profile,
            COALESCE(
                (SELECT json_agg(json_build_object('id', g.id, 'name', g.name))
                 FROM accounts.user_group_memberships m
                 JOIN accounts.user_groups g ON m.group_id = g.id
                 WHERE m.user_id = u.id AND m.is_active = TRUE),
                '[]'::JSON
            ) AS groups,
            COALESCE(
                (SELECT json_agg(json_build_object('id', c.id, 'type', ct.name, 'value', c.value))
                 FROM accounts.user_contacts c
                 JOIN accounts.contact_types ct ON c.contact_type_id = ct.id
                 WHERE c.user_id = u.id AND c.is_active = TRUE),
                '[]'::JSON
            ) AS contacts
        FROM accounts.users u
        WHERE u.id = v_user_id AND u.is_active = TRUE;
        RETURN;
    END IF;

    -- 3. Проверка формата (только если не UUID)
    v_is_phone := identifier ~ '^\+[1-9]\d{1,14}$';  -- E.164 (например, +79991234567)
    v_is_email := identifier ~ '^[^@]+@[^@]+\.[^@]+$'; -- базовая проверка email

    -- 4. Поиск по контактам
    RETURN QUERY
    SELECT
        u.id,
        u.created_at,
        u.updated_at,
        u.is_active,
        u.profile,
        COALESCE(
            (SELECT json_agg(json_build_object('id', g.id, 'name', g.name))
             FROM accounts.user_group_memberships m
             JOIN accounts.user_groups g ON m.group_id = g.id
             WHERE m.user_id = u.id AND m.is_active = TRUE),
            '[]'::JSON
        ) AS groups,
        COALESCE(
            (SELECT json_agg(json_build_object('id', c.id, 'type', ct.name, 'value', c.value))
             FROM accounts.user_contacts c
             JOIN accounts.contact_types ct ON c.contact_type_id = ct.id
             WHERE c.user_id = u.id AND c.is_active = TRUE),
            '[]'::JSON
        ) AS contacts
    FROM accounts.users u
    JOIN accounts.user_contacts c ON u.id = c.user_id
    JOIN accounts.contact_types ct ON c.contact_type_id = ct.id
    WHERE
        c.value = identifier
        AND c.is_active = TRUE
        AND u.is_active = TRUE
        AND (
            (v_is_phone AND ct.name = 'phone')
            OR (v_is_email AND ct.name = 'email')
            OR (NOT v_is_phone AND NOT v_is_email AND ct.name = 'second_login')
        )
    LIMIT 1;  -- На случай дублей (по бизнес-логике их не должно быть)
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000