DROP VIEW IF EXISTS c2c_ytd_dpt;

CREATE OR REPLACE VIEW c2c_ytd_dpt AS 
 SELECT aml.id AS aml_id,
    am.id AS am_id,
    aml.analytic_account_id,
    aml.account_id,
    aml.journal_id,
    aj.name,
    aa.code,
    aa.parent_id,
    aac.name AS project_name,
    aac.state AS project_status,
    aac_dept.name AS proj_department,
    aml_company.name AS company,
    am.name AS am_name,
    am.ref AS am_ref,
    aml.name AS aml_name,
    am.date AS move_date,
    aml.date AS move_line_date,
    aml.period_id,
    to_char(aml.date::timestamp with time zone, 'yyyy'::text) AS move_line_year,
    to_char(aml.date::timestamp with time zone, 'MM'::text) AS move_line_month,
    to_char(aml.date::timestamp with time zone, 'yyyy-MM'::text) AS move_line_year_month,
    ( SELECT res_currency.name
           FROM res_currency
          WHERE res_currency.id = aml_company.currency_id) AS cie_currency,
    ( SELECT res_currency.name
           FROM res_currency
          WHERE res_currency.id = aml.currency_id) AS aml_currency,
    aml.tax_amount,
    aml.amount_currency,
    aml.credit - aml.debit AS amount_real,
    parent_account.code AS groupe_account_code,
    parent_account.name AS groupe_account_name
   FROM account_move_line aml
     LEFT JOIN ( SELECT rel.budget_item_id,
            rel.account_account_id,
            bi.code,
            bi.name,
            account.parent_left,
            account.parent_right
           FROM account_account_budget_item_rel rel,
            budget_item bi,
            account_account account
          WHERE rel.account_account_id = account.id AND bi.id = rel.budget_item_id) parent_account ON parent_account.parent_left < (( SELECT account_account.parent_left
           FROM account_account
          WHERE account_account.id = aml.account_id)) AND parent_account.parent_right > (( SELECT account_account.parent_left
           FROM account_account
          WHERE account_account.id = aml.account_id))
     LEFT JOIN account_analytic_account aac ON aml.analytic_account_id = aac.id
     LEFT JOIN hr_department aac_dept ON aac.department_id = aac_dept.id,
    res_company aml_company,
    account_move am,
    account_journal aj,
    account_account aa
  WHERE aml.analytic_account_id > 0 AND aml.move_id = am.id AND aml.journal_id = aj.id
  AND aml.company_id = aml_company.id AND aml.account_id = aa.id
  AND (to_number(to_char('now'::date::timestamp without time zone, 'yyyy'::text), '9999'::text) - 
    to_number(to_char(aml.date::timestamp without time zone, 'yyyy'::text), '9999'::text)) <= 2::numeric;

