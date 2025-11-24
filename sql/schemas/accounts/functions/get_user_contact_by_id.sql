CREATE OR REPLACE FUNCTION "accounts"."get_user_contact_by_id"("p_id" uuid)
  RETURNS "accounts"."user_contacts" AS $BODY$
DECLARE
    result_record "accounts"."user_contacts";
BEGIN
    SELECT * INTO result_record
    FROM "accounts"."user_contacts"
    WHERE "id" = p_id;

    IF NOT FOUND THEN
        RETURN NULL;  -- или RAISE EXCEPTION, если предпочтёшь
    END IF;

    RETURN result_record;
END;
$BODY$
  LANGUAGE plpgsql STABLE
  COST 100