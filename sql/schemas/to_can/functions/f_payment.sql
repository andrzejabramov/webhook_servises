CREATE OR REPLACE FUNCTION "to_can"."f_payment"("x_ins" jsonb)
  RETURNS "pg_catalog"."json" AS $BODY$
BEGIN
    WITH
    input_data AS (
        SELECT
            x_ins AS raw_input,
            (x_ins ->> 'MID')::text AS mid,
            (x_ins ->> 'Amount')::numeric AS amount,
            (x_ins ->> 'Id') AS billid,
            LEFT(x_ins ->> 'PaidAt', 4)::integer AS year
    ),
    merchant_tap AS (
        SELECT
            i.*,
            (mt.accesuaries ->> 'account')::text AS privilege,
            mt.syspay_merch::integer AS idmerch
        FROM input_data i
        JOIN to_can.merchant_tap2go mt ON mt.mid = i.mid
    ),
    firm_and_service AS (
        SELECT
            mt.*,
            fs.fljson_firm,
            fs.idcommparam,
            fs.service,
            LEFT(mt.privilege, 6)::char(6) AS firm
        FROM merchant_tap mt
        JOIN common.firmservice fs ON fs.idfirm = LEFT(mt.privilege, 6)
    ),
    comm_and_user AS (
        SELECT
            fs.*,
            cp.json_commparam,
            u.attributies AS login_attribs
        FROM firm_and_service fs
        JOIN common.commparam cp
            ON cp.idcommparam = fs.idcommparam AND cp."enable" = TRUE
        LEFT JOIN auth.users u
            ON u.login_master = (fs.fljson_firm ->> 'login')::text
    ),
    merchant_details AS (
        SELECT
            cu.*,
            m.accesuaries AS merch_accesuaries,
            (m.accesuaries ->> 'format_amount')::numeric AS ratio
        FROM comm_and_user cu
        JOIN common.merchant m ON m.idmerch = cu.idmerch
    ),
    calculated_sum AS (
        SELECT
            md.*,
            (md.amount * md.ratio)::numeric(10,2) AS sum_val
        FROM merchant_details md
    ),
    matched_tarif AS (
        SELECT
            cs.*,
            tt."Tarif" AS idtarif
        FROM calculated_sum cs
        JOIN common.tranztarif tt
            ON tt."Firm" = cs.firm
            AND tt."Syspay" = cs.idmerch
            AND tt."Enable" = 1
        JOIN common.breakesum bs
            ON tt."Breakesum" = bs.idbreake
        WHERE
            cs.sum_val > (bs.json_breakesum ->> 'Minsum')::numeric
            AND cs.sum_val < (bs.json_breakesum ->> 'Maxsum')::numeric
    ),
    tarif_json AS (
        SELECT
            mt.*,
            t.json_tarif
        FROM matched_tarif mt
        LEFT JOIN common.tarif t ON t.idtarif = mt.idtarif
    ),
    ekassa_info AS (
        SELECT
            tj.*,
            mi.ecassa::jsonb AS ekassa_raw
        FROM tarif_json tj
        LEFT JOIN mytosb.info mi
            ON mi.syspay = tj.idmerch AND mi.service = tj.service
    ),
    channel_data AS (
        SELECT
            ei.*,
            ek.channel_notify
        FROM ekassa_info ei
        LEFT JOIN ekassa.ekassa ek
            ON ek.id_kass = (ei.ekassa_raw -> 'ecassa' ->> 0)::integer
    ),
    final_payload AS (
        SELECT
            (raw_input ||
             jsonb_build_object('id_paybank', billid, 'principal', privilege)
            ) - 'RRN' - 'TID' - 'Card' - 'Device' - 'Invoice' - 'MIDName' -
              'BranchID' - 'CardType' - 'EventType' - 'Operation' -
              'BranchName' - 'DvcAppBuild' - 'OfflineMode' - 'PaymentService'
            AS data_json,
            year,
            jsonb_build_object('id_order', billid, 'merch', idmerch) AS idpaymerch,
            json_commparam AS comm_json,
            (fljson_firm::jsonb || COALESCE(login_attribs::jsonb, '{}'::jsonb)) AS firm_json,
            merch_accesuaries AS merch_json,
            json_tarif AS tarif_json,
            ekassa_raw AS e_kassa
        FROM channel_data
    )
    INSERT INTO reports.payment (
        data_json, year, idpaymerch, comm_json, firm_json, merch_json, tarif_json, e_kassa
    )
    SELECT
        data_json, year, idpaymerch, comm_json, firm_json, merch_json, tarif_json, e_kassa
    FROM final_payload
    ON CONFLICT DO NOTHING;

    -- Возвращаем исходный JSON — для стабильности и совместимости
    RETURN x_ins;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 300