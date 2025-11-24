CREATE OR REPLACE FUNCTION "accounts"."get_users_paginated"("p_limit" int4, "p_offset" int4)
  RETURNS TABLE("id" uuid, "username" text, "is_active" bool, "created_at" timestamptz, "updated_at" timestamptz, "profile" jsonb) AS $BODY$
BEGIN
    RETURN QUERY
    SELECT
        u.id,
        u.username,
        u.is_active,
        u.created_at,
        u.updated_at,
        u.profile
    FROM accounts.users u
    ORDER BY u.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000