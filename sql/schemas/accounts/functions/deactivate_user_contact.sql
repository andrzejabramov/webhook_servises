CREATE OR REPLACE FUNCTION "accounts"."deactivate_user_contact"("p_id" uuid)
  RETURNS "accounts"."user_contacts" AS $BODY$
DECLARE
    updated_record "accounts"."user_contacts";
BEGIN
    UPDATE "accounts"."user_contacts"
    SET "is_active" = false,
        "updated_at" = now()
    WHERE "id" = p_id
    RETURNING * INTO updated_record;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'User contact % not found', p_id;
    END IF;

    RETURN updated_record;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100