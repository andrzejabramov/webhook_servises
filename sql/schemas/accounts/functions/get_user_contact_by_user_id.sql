CREATE OR REPLACE FUNCTION "accounts"."get_user_contacts_by_user_id"("p_user_id" uuid, "p_only_active" bool=true)
  RETURNS SETOF "accounts"."user_contacts" AS $BODY$
BEGIN
    RETURN QUERY
    SELECT *
    FROM "accounts"."user_contacts"
    WHERE "user_id" = p_user_id
      AND ("is_active" = true OR NOT p_only_active)
    ORDER BY "created_at" DESC;
END;
$BODY$
  LANGUAGE plpgsql STABLE
  COST 100
  ROWS 1000