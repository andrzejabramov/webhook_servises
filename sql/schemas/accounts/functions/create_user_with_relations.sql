CREATE OR REPLACE FUNCTION "accounts"."create_user_with_relations"("p_payload" jsonb)
  RETURNS "accounts"."users" AS $BODY$
DECLARE
    new_user accounts.users;
    v_second_login TEXT;
    v_phone TEXT;
    v_email TEXT;
    v_profile JSONB;
    v_password_hash TEXT;
    v_group_names TEXT[];
    v_contact_type_id INT;
    group_name TEXT;
    v_group_id INT2;
BEGIN
    -- Валидация обязательных полей
    v_second_login := p_payload->>'second_login';
    v_phone := p_payload->>'phone';
    v_password_hash := p_payload->>'password_hash';
    v_group_names := ARRAY(SELECT jsonb_array_elements_text(p_payload->'group_names'));

    IF v_second_login IS NULL OR v_second_login = '' THEN
        RAISE EXCEPTION 'Field "second_login" is required';
    END IF;
    IF v_phone IS NULL OR v_phone = '' THEN
        RAISE EXCEPTION 'Field "phone" is required';
    END IF;
    IF v_password_hash IS NULL THEN
        RAISE EXCEPTION 'Field "password_hash" is required';
    END IF;
    IF v_group_names IS NULL OR array_length(v_group_names, 1) = 0 THEN
        RAISE EXCEPTION 'Field "group_names" must be a non-empty array';
    END IF;

    -- Опциональные поля
    v_email := NULLIF(p_payload->>'email', '');
    v_profile := p_payload->'profile';

    -- Создаём пользователя
    INSERT INTO accounts.users (profile, password_hash)
    VALUES (v_profile, v_password_hash)
    RETURNING * INTO new_user;

    -- second_login
    SELECT id INTO v_contact_type_id FROM accounts.contact_types WHERE name = 'second_login';
    IF NOT FOUND THEN RAISE EXCEPTION 'Contact type "second_login" not found'; END IF;
    PERFORM accounts.create_user_contact(new_user.id, v_contact_type_id, v_second_login);

    -- phone
    SELECT id INTO v_contact_type_id FROM accounts.contact_types WHERE name = 'phone';
    IF NOT FOUND THEN RAISE EXCEPTION 'Contact type "phone" not found'; END IF;
    PERFORM accounts.create_user_contact(new_user.id, v_contact_type_id, v_phone);

    -- email (опционально)
    IF v_email IS NOT NULL THEN
        SELECT id INTO v_contact_type_id FROM accounts.contact_types WHERE name = 'email';
        IF NOT FOUND THEN RAISE EXCEPTION 'Contact type "email" not found'; END IF;
        PERFORM accounts.create_user_contact(new_user.id, v_contact_type_id, v_email);
    END IF;

    -- Назначение групп
    FOREACH group_name IN ARRAY v_group_names
    LOOP
        SELECT id INTO v_group_id
        FROM accounts.user_groups
        WHERE name = group_name AND is_active = true;
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Active user group "%" not found', group_name;
        END IF;
        PERFORM accounts.add_user_to_group(new_user.id, v_group_id);
    END LOOP;

    RETURN new_user;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100