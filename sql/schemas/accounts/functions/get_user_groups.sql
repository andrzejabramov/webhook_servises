CREATE OR REPLACE FUNCTION "accounts"."get_user_groups"("p_user_id" uuid)
  RETURNS SETOF "accounts"."user_groups" AS $BODY$
    SELECT g.*
    FROM accounts.user_groups g
    JOIN accounts.user_group_memberships m ON g.id = m.group_id
    WHERE m.user_id = p_user_id AND m.is_active = true
    ORDER BY g.name;
$BODY$
  LANGUAGE sql VOLATILE
  COST 100
  ROWS 1000