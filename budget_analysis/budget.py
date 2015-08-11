# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Laurent Meuwly
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp import tools
from openerp.modules import get_module_resource


class budget_analysis(orm.Model):
    _name = "budget.analysis"
    _description = "Budget analysis"
    _auto = False

    def init(self, cr):
        
        sql_path = get_module_resource('budget_analysis', 'sql',
                                       'function_c2c_xrate_conversion.sql')
        with file(sql_path) as sql_file:
            cr.execute(sql_file.read())

        sql_path = get_module_resource('budget_analysis', 'sql',
                                       'view_c2c_ytd_dpt.sql')
        with file(sql_path) as sql_file:
            cr.execute(sql_file.read())

        sql_path = get_module_resource('budget_analysis', 'sql',
                                       'view_c2c_budget_analytic.sql')
        with file(sql_path) as sql_file:
            cr.execute(sql_file.read())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4;
