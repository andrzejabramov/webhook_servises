CREATE OR REPLACE FUNCTION "to_can"."f_syspay"("x_json" json)
  RETURNS "pg_catalog"."json" AS $BODY$
	DECLARE
		xans JSON DEFAULT '{"ans":"ok"}' ;
		xid UUID;
		inserted_rows INTEGER;
		xjson JSONB;
	--input data:
	--{
    --}
BEGIN
	xid := (x_json::jsonb ->> 'Id')::uuid;
	INSERT INTO "to_can".syspay (json_inside, id_uuid)
    VALUES (x_json, xid)
    ON CONFLICT (id_uuid) DO NOTHING;

    GET DIAGNOSTICS inserted_rows = ROW_COUNT;

    IF inserted_rows = 0 THEN
        xans := json_build_object('ans', 'duplicated', 'id', xid);
		ELSE
				xjson := x_json::jsonb;
				xans := to_can.f_payment(xjson);
        --xans := json_build_object('ans', 'ok', 'id', xid);
    END IF;

    RETURN xans;
END;
--output data:
--{"ans": "ok"}
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100