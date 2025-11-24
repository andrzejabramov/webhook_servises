CREATE OR REPLACE FUNCTION "accounts"."create_user_contact"("p_user_id" uuid, "p_contact_type_id" int4, "p_value" text)
  RETURNS "accounts"."user_contacts" AS $BODY$
DECLARE
    new_record "accounts"."user_contacts";
BEGIN
    -- Проверим, существует ли пользователь и тип контакта (необязательно, но безопасно)
    IF NOT EXISTS (SELECT 1 FROM "accounts"."users" WHERE "id" = "p_user_id") THEN
        RAISE EXCEPTION 'User % not found', "p_user_id";
    END IF;

    IF NOT EXISTS (SELECT 1 FROM "accounts"."contact_types" WHERE "id" = "p_contact_type_id") THEN
        RAISE EXCEPTION 'Contact type % not found', "p_contact_type_id";
    END IF;

    -- 🔑 КЛЮЧЕВОЕ ДОПОЛНЕНИЕ: деактивируем все предыдущие активные контакты этого типа для пользователя
    UPDATE "accounts"."user_contacts"
    SET "is_active" = false,
        "updated_at" = now()
    WHERE "user_id" = "p_user_id"
      AND "contact_type_id" = "p_contact_type_id"
      AND "is_active" = true;

    -- Вставляем новый контакт (без ON CONFLICT по значению — допускаем дубли значений, если они не активны)
    INSERT INTO "accounts"."user_contacts" (
        "user_id",
        "contact_type_id",
        "value",
        "is_active"
    )
    VALUES (
        "p_user_id",
        "p_contact_type_id",
        "p_value",
        true  -- всегда активен при создании
    )
    RETURNING * INTO new_record;

    RETURN new_record;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100