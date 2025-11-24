CREATE OR REPLACE FUNCTION "accounts"."update_user_group"("p_id" int2, "p_name" text=NULL::text, "p_description" text=NULL::text, "p_is_active" bool=NULL::boolean)
  RETURNS "accounts"."user_groups" AS $BODY$
DECLARE
    updated_row accounts.user_groups;
BEGIN
    UPDATE accounts.user_groups
    SET
        name = COALESCE(p_name, name),
        description = COALESCE(p_description, description),
        is_active = COALESCE(p_is_active, is_active),
        updated_at = now()
    WHERE id = p_id
    RETURNING * INTO updated_row;

    RETURN updated_row;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100