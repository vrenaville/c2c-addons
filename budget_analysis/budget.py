# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Camptocamp SA
# @author Laurent Meuwly
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import orm, fields
from openerp import tools

class budget_analysis(orm.Model):
    _name = "budget.analysis"
    _description = "Budget analysis"
    _auto = False

    def init(self, cr):
        cr.execute("""
            -- Drop old existing view if exist
            DROP FUNCTION IF EXISTS c2c_xrate_conversion(integer,integer,double precision,date);
            CREATE OR REPLACE FUNCTION c2c_xrate_conversion(currency_id_base integer, currency_id_dest integer, value_base double precision, conversion_date date, out xrate numeric, out value_dest double precision)
AS
$BODY$

DECLARE
    rcur RECORD; -- DB cursor to handle the result

    xrate_base numeric;
    xrate_dest numeric;

BEGIN
        -- The exchange rate is a ratio between source currency rate and destination currency rate, not necessarily at the same date
	    -- This way of calculation makes the function independent from the company currency, as we don't obviously know it here

        -- if destination currency and source currency are the same, just take the input values as it
        if currency_id_base = currency_id_dest
        then
                xrate := 1;
                value_dest := value_base;
        else
        		-- read the last rate for source currency
        		FOR rcur IN SELECT rate FROM res_currency_rate WHERE currency_id=currency_id_base AND name <= conversion_date ORDER BY name DESC LIMIT 1 LOOP
        			xrate_base = rcur.rate;
        		END LOOP;

                -- read the last rate for destination currency
        		FOR rcur IN SELECT rate FROM res_currency_rate WHERE currency_id=currency_id_dest AND name <= conversion_date ORDER BY name DESC LIMIT 1 LOOP
        			xrate_dest = rcur.rate;
        		END LOOP;

                xrate:= xrate_dest / xrate_base;
                value_dest := value_base * xrate;

        end if;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
        """)

        cr.execute("""
        DROP VIEW IF EXISTS c2c_ytd_dpt;
        CREATE OR REPLACE VIEW c2c_ytd_dpt AS
 SELECT ail.account_analytic_id,
    ail.account_id,
    aa.code,
    aa.parent_id,
    aac.name AS project_name,
    aac.state AS project_status,
    aac_dept.name AS proj_department,
    ai_company.name AS company,
    ai.name,
    ai.internal_number,
    ai.type,
    ai.date_invoice,
    ai.period_id,
    to_char(ai.date_invoice::timestamp with time zone, 'yyyy'::text) AS invoice_year,
    to_char(ai.date_invoice::timestamp with time zone, 'MM'::text) AS invoice_month,
    to_char(ai.date_invoice::timestamp with time zone, 'yyyy-MM'::text) AS invoice_year_month,
    ail.price_subtotal,
        CASE
            WHEN ai.type::text = 'out_refund'::text THEN (-1)::numeric * ail.price_subtotal
            ELSE ail.price_subtotal
        END AS amount,
    ai_currency.name AS currency,
    ( SELECT c2c_xrate_conversion.xrate
           FROM c2c_xrate_conversion(ai_currency.id, ( SELECT res_currency.id
                   FROM res_currency
                  WHERE res_currency.name::text = 'CHF'::text), ail.price_subtotal::double precision, 'now'::text::date) c2c_xrate_conversion(xrate, value_dest)) AS xrate,
    ( SELECT c2c_xrate_conversion.value_dest AS amount_real
           FROM c2c_xrate_conversion(ai_currency.id, ( SELECT res_currency.id
                   FROM res_currency
                  WHERE res_currency.name::text = 'CHF'::text),
                CASE
                    WHEN ai.type::text = 'out_refund'::text THEN (-1)::numeric * ail.price_subtotal
                    ELSE ail.price_subtotal
                END::double precision, 'now'::text::date) c2c_xrate_conversion(xrate, value_dest)) AS amount_real,
    parent_account.code AS groupe_account_code,
    parent_account.name AS groupe_account_name
   FROM account_invoice_line ail
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
          WHERE account_account.id = ail.account_id)) AND parent_account.parent_right > (( SELECT account_account.parent_left
           FROM account_account
          WHERE account_account.id = ail.account_id))
     LEFT JOIN account_analytic_account aac ON ail.account_analytic_id = aac.id
     LEFT JOIN hr_department aac_dept ON aac.department_id = aac_dept.id,
    account_invoice ai,
    res_currency ai_currency,
    res_company ai_company,
    account_account aa
  WHERE ail.invoice_id = ai.id AND (ai.state::text = ANY (ARRAY['open'::character varying, 'paid'::character varying]::text[])) AND ai.currency_id = ai_currency.id AND ai.company_id = ai_company.id AND ail.account_id = aa.id AND to_char(ai.date_invoice::timestamp with time zone, 'yyyy'::text) = to_char('now'::text::date::timestamp with time zone, 'yyyy'::text);

    """)



        cr.execute("""
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
           FROM c2c_xrate_conversion(bl.currency_id, 1, bl.amount, 'now'::text::date) c2c_xrate_conversion(xrate, value_dest)) AS xrate,
    ( SELECT c2c_xrate_conversion.value_dest AS amount_real_chf
           FROM c2c_xrate_conversion(bl.currency_id, 1, bl.amount, 'now'::text::date) c2c_xrate_conversion(xrate, value_dest)) AS amount_real_chf
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
  """)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

