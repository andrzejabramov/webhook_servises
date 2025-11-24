CREATE OR REPLACE FUNCTION "accounts"."get_users_with_relations"("p_limit" int4, "p_offset" int4)
  RETURNS TABLE("id" uuid, "username" text, "is_active" bool, "created_at" timestamptz, "updated_at" timestamptz, "profile" jsonb, "contacts" jsonb, "groups" _text) AS $BODY$
BEGIN
    RETURN QUERY
    SELECT
        u.id,
        u.username,
        u.is_active,
        u.created_at,
        u.updated_at,
        u.profile,
        -- Агрегируем контакты: contact_type.name → contact_value
        jsonb_object_agg(
            ct.name,
            uc.value
        ) FILTER (WHERE uc.id IS NOT NULL) AS contacts,
        -- Агрегируем группы: массив имён
        ARRAY_AGG(ug.name) FILTER (WHERE ug.id IS NOT NULL) AS groups
    FROM accounts.users u
    -- Контакты
    LEFT JOIN accounts.user_contacts uc
        ON u.id = uc.user_id AND uc.is_active = true
    LEFT JOIN accounts.contact_types ct
        ON uc.contact_type_id = ct.id
    -- Группы
    LEFT JOIN accounts.user_group_memberships m
        ON u.id = m.user_id AND m.is_active = true
    LEFT JOIN accounts.user_groups ug
        ON m.group_id = ug.id
    GROUP BY u.id, u.username, u.is_active, u.created_at, u.updated_at, u.profile
    ORDER BY u.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000