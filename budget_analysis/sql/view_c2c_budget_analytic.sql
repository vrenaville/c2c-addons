DROP VIEW IF EXISTS c2c_budget_analytic;

CREATE OR REPLACE VIEW c2c_budget_analytic AS 
 SELECT
        CASE
            WHEN bl.date_start IS NULL THEN 'now'::text::date
            ELSE bl.date_start
        END AS date_start,
    aac.name AS project_name,
    bl.name AS "desc",
    res_company.name AS company,
    aac_dept.name AS proj_department,
    res_partner.name AS partner_name,
    proj_manager.login AS proj_manager,
    aac.state AS project_status,
    bi.name AS groupe_account_parent,
    budget_item.name AS groupe_account_name,
    budget_item.code AS groupe_account_code,
    budget_version.name AS budget_version,
    to_char(bl.date_start::timestamp with time zone, 'yyyy'::text) AS prest_year,
    to_char(bl.date_start::timestamp with time zone, 'MM'::text) AS prest_month,
    to_char(bl.date_start::timestamp with time zone, 'yyyy-MM'::text) AS prest_year_month,
    bl.amount AS amount_real_curr,
    bl_currency.name AS bl_currency,
    ( SELECT c2c_xrate_conversion.xrate
           FROM c2c_xrate_conversion(bl.currency_id, ( SELECT res_currency.id
                   FROM res_currency
                  WHERE res_currency.name::text = 'CHF'::text), bl.amount, 'now'::text::date) c2c_xrate_conversion(xrate, value_dest)) AS xrate,
    ( SELECT c2c_xrate_conversion.value_dest
           FROM c2c_xrate_conversion(bl.currency_id, ( SELECT res_currency.id
                   FROM res_currency
                  WHERE res_currency.name::text = 'CHF'::text), bl.amount, 'now'::text::date) c2c_xrate_conversion(xrate, value_dest)) AS amount_real_chf
   FROM budget_line bl
     LEFT JOIN account_analytic_account aac ON bl.analytic_account_id = aac.id
     LEFT JOIN res_company ON aac.company_id = res_company.id
     LEFT JOIN hr_department aac_dept ON aac.department_id = aac_dept.id
     LEFT JOIN res_partner ON aac.partner_id = res_partner.id
     LEFT JOIN res_users proj_manager ON aac.user_id = proj_manager.id,
    budget_item,
    budget_item bi,
    budget_version,
    res_currency bl_currency
  WHERE bl.budget_item_id = budget_item.id AND bl.budget_version_id = budget_version.id AND budget_item.parent_id = bi.id AND bl.currency_id = bl_currency.id;

