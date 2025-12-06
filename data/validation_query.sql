WITH

-- ============================================================
-- 1) Core NACC Detail (base record)
-- ============================================================
detail AS (
    SELECT
        nacc_id,
        doc_id,
        title AS nd_title,
        first_name AS nd_first_name,
        last_name AS nd_last_name,
        position AS nd_position,
        submitted_case,
        submitted_date,
        disclosure_announcement_date,
        disclosure_start_date,
        disclosure_end_date,
        date_by_submitted_case,
        royal_start_date,
        submitter_id as ref_id,
        agency
    FROM nacc_detail
),

-- ============================================================
-- 2) Submitter info (1 row per nacc_id)
-- ============================================================
submitter AS (
    SELECT
        submitter_id,
        title AS submitter_title,
        first_name AS submitter_first_name,
        last_name AS submitter_last_name,
        age AS submitter_age,
        status AS submitter_marital_status,
        status_date AS submitter_status_date,
        status_month AS submitter_status_month,
        status_year AS submitter_status_year,
        sub_district AS submitter_sub_district,
        district AS submitter_district,
        province AS submitter_province,
        post_code AS submitter_post_code,
        phone_number AS submitter_phone_number,
        mobile_number AS submitter_mobile_number,
        email AS submitter_email
    FROM submitter_info
),

-- ============================================================
-- 3) Spouse info (0–1 rows per nacc_id)
-- ============================================================
spouse AS (
    SELECT
        nacc_id,
        spouse_id,
        title AS spouse_title,
        first_name AS spouse_first_name,
        last_name AS spouse_last_name,
        age AS spouse_age,
        status AS spouse_status,
        status_date AS spouse_status_date,
        status_month AS spouse_status_month,
        status_year AS spouse_status_year
    FROM spouse_info
),

-- ============================================================
-- 4) Statement totals (valuation)
-- ============================================================
statement_totals AS (
    SELECT
        nacc_id,
        SUM(valuation_submitter) AS statement_valuation_submitter_total,
        SUM(valuation_spouse) AS statement_valuation_spouse_total,
        SUM(valuation_child) AS statement_valuation_child_total
    FROM statement
    GROUP BY nacc_id
),

-- ============================================================
-- 5) Statement detail aggregates
-- ============================================================
detail_totals AS (
    SELECT
        nacc_id,
        COUNT(*) AS statement_detail_count,
        MAX(CASE WHEN note IS NULL OR TRIM(note) = '' THEN 0 ELSE 1 END) AS has_statement_detail_note
    FROM statement_detail
    GROUP BY nacc_id
),

-- ============================================================
-- 6) Asset counts by subtype
-- ============================================================
asset_counts AS (
    SELECT
        nacc_id,
        COUNT(*) AS asset_count
    FROM asset
    GROUP BY nacc_id
),

asset_land AS (
    SELECT nacc_id, COUNT(*) AS asset_land_count
    FROM asset_land_info
    GROUP BY nacc_id
),

asset_building AS (
    SELECT nacc_id, COUNT(*) AS asset_building_count
    FROM asset_building_info
    GROUP BY nacc_id
),

asset_vehicle AS (
    SELECT nacc_id, COUNT(*) AS asset_vehicle_count
    FROM asset_vehicle_info
    GROUP BY nacc_id
),

asset_other AS (
    SELECT nacc_id, SUM(count) AS asset_other_count
    FROM asset_other_asset_info
    GROUP BY nacc_id
),

-- ============================================================
-- 7) Asset valuation per type (using asset_type)
-- ============================================================
asset_val AS (
    SELECT
        a.nacc_id,
        SUM(a.valuation) AS asset_total_valuation_amount,
        SUM(CASE WHEN t.asset_type_main_type_name = 'ที่ดิน'
                 THEN a.valuation ELSE 0 END) AS asset_land_valuation_amount,
        SUM(CASE WHEN t.asset_type_main_type_name = 'สิ่งปลูกสร้าง'
                 THEN a.valuation ELSE 0 END) AS asset_building_valuation_amount,
        SUM(CASE WHEN t.asset_type_main_type_name = 'ยานพาหนะ'
                 THEN a.valuation ELSE 0 END) AS asset_vehicle_valuation_amount,
        SUM(CASE WHEN t.asset_type_main_type_name NOT IN ('ที่ดิน','สิ่งปลูกสร้าง','ยานพาหนะ')
                 THEN a.valuation ELSE 0 END) AS asset_other_asset_valuation_amount,
        SUM(CASE WHEN a.owner_by_submitter THEN a.valuation ELSE 0 END) AS asset_valuation_submitter_amount,
        SUM(CASE WHEN a.owner_by_spouse THEN a.valuation ELSE 0 END) AS asset_valuation_spouse_amount,
        SUM(CASE WHEN a.owner_by_child THEN a.valuation ELSE 0 END) AS asset_valuation_child_amount
    FROM asset a
    LEFT JOIN asset_type t ON a.asset_type_id = t.asset_type_id
    GROUP BY a.nacc_id
),

-- ============================================================
-- 8) Relatives
-- ============================================================
rel AS (
    SELECT
        nacc_id,
        COUNT(*) AS relative_count,
        MAX(CASE WHEN is_death THEN 1 ELSE 0 END) AS relative_has_death_flag
    FROM relative_info
    GROUP BY nacc_id
)

-- ============================================================
-- 9) FINAL SELECT (flattened)
-- ============================================================
SELECT
    d.nacc_id,

    -- nacc_detail
    d.doc_id, d.nd_title, d.nd_first_name, d.nd_last_name, d.nd_position, d.submitted_date,
    d.disclosure_announcement_date, d.disclosure_start_date, d.disclosure_end_date,d.date_by_submitted_case,d.royal_start_date,
    d.agency,

    -- submitter_info
    s.submitter_id, s.submitter_title, s.submitter_first_name, s.submitter_last_name,
    s.submitter_age, s.submitter_marital_status,
    s.submitter_status_date, s.submitter_status_month, s.submitter_status_year,
    s.submitter_sub_district, s.submitter_district, s.submitter_province, s.submitter_post_code,
    s.submitter_phone_number, s.submitter_mobile_number, s.submitter_email,

    -- spouse_info
    sp.spouse_id, sp.spouse_title, sp.spouse_first_name, sp.spouse_last_name,
    sp.spouse_age, sp.spouse_status, sp.spouse_status_date, sp.spouse_status_month, sp.spouse_status_year,

    -- statement totals
    st.statement_valuation_submitter_total,
    st.statement_valuation_spouse_total,
    st.statement_valuation_child_total,

    -- statement detail
    dt.statement_detail_count,
    dt.has_statement_detail_note,

    -- assets counts
    ac.asset_count,
    al.asset_land_count,
    ab.asset_building_count,
    av.asset_vehicle_count,
    ao.asset_other_count,

    -- asset valuations
    avl.asset_total_valuation_amount,
    avl.asset_land_valuation_amount,
    avl.asset_building_valuation_amount,
    avl.asset_vehicle_valuation_amount,
    avl.asset_other_asset_valuation_amount,
    avl.asset_valuation_submitter_amount,
    avl.asset_valuation_spouse_amount,
    avl.asset_valuation_child_amount,

    -- relatives
    r.relative_count,
    r.relative_has_death_flag

FROM detail d
LEFT JOIN submitter s ON d.ref_id = s.submitter_id
LEFT JOIN spouse sp ON d.nacc_id = sp.nacc_id
LEFT JOIN statement_totals st ON d.nacc_id = st.nacc_id
LEFT JOIN detail_totals dt ON d.nacc_id = dt.nacc_id
LEFT JOIN asset_counts ac ON d.nacc_id = ac.nacc_id
LEFT JOIN asset_land al ON d.nacc_id = al.nacc_id
LEFT JOIN asset_building ab ON d.nacc_id = ab.nacc_id
LEFT JOIN asset_vehicle av ON d.nacc_id = av.nacc_id
LEFT JOIN asset_other ao ON d.nacc_id = ao.nacc_id
LEFT JOIN asset_val avl ON d.nacc_id = avl.nacc_id
LEFT JOIN rel r ON d.nacc_id = r.nacc_id

ORDER BY d.nacc_id;
