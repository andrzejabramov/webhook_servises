CREATE OR REPLACE FUNCTION "accounts"."create_user_bulk_stub"("p_payload" jsonb)
  RETURNS TABLE("status" text, "user_id" uuid) AS $BODY$
DECLARE
    v_phone TEXT;
    v_group_names TEXT[];
    v_exists BOOLEAN;
    v_new_user_id UUID;
    v_contact_type_id INT;
    group_name TEXT;
    v_group_id INT2;
BEGIN
    -- Обязательные поля для bulk
    v_phone := NULLIF(p_payload->>'phone', '');
    v_group_names := ARRAY(SELECT jsonb_array_elements_text(p_payload->'group_names'));

    IF v_phone IS NULL THEN
        RAISE EXCEPTION 'Field "phone" is required';
    END IF;
    IF v_group_names IS NULL OR array_length(v_group_names, 1) = 0 THEN
        RAISE EXCEPTION 'Field "group_names" must be a non-empty array';
    END IF;

    -- Проверка: существует ли активный контакт с таким phone?
    SELECT EXISTS(
        SELECT 1
        FROM accounts.contacts c
        JOIN accounts.contact_types ct ON c.contact_type_id = ct.id
        WHERE ct.name = 'phone'
          AND c.value = v_phone
          AND c.is_active = true
    ) INTO v_exists;

    IF v_exists THEN
        status := 'skipped';
        user_id := NULL;
        RETURN NEXT;
        RETURN;
    END IF;

    -- Создаём пользователя БЕЗ пароля и second_login
    INSERT INTO accounts.users (profile, password_hash)
    VALUES (p_payload->'profile', NULL)  -- password_hash = NULL!
    RETURNING id INTO v_new_user_id;

    -- Добавляем контакт: phone
    SELECT id INTO v_contact_type_id FROM accounts.contact_types WHERE name = 'phone';
    IF NOT FOUND THEN RAISE EXCEPTION 'Contact type "phone" not found'; END IF;
    PERFORM accounts.create_user_contact(v_new_user_id, v_contact_type_id, v_phone);

    -- Назначение групп (ролей)
    FOREACH group_name IN ARRAY v_group_names
    LOOP
        SELECT id INTO v_group_id
        FROM accounts.user_groups
        WHERE name = group_name AND is_active = true;
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Active user group "%" not found', group_name;
        END IF;
        PERFORM accounts.add_user_to_group(v_new_user_id, v_group_id);
    END LOOP;

    status := 'created';
    user_id := v_new_user_id;
    RETURN NEXT;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000