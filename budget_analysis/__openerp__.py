# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2014 Camptocamp SA (http://www.camptocamp.com)
#   @author Laurent Meuwly
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

{
    'name' : 'Specific SQL views for budget analysis',
    'version' : '1.0.0',
    'category' : 'finance',
    'description' : """
    
Advanced budget analysis
========================

Following views are added to provide detailled informations regarding budget.
Actually there is no internal views to show the result, as the informations are exploited through some BI cube.
It is recommended to use Excel Sheet and its Pivot tables to gain all analytic capabilities.

[Add some documentation link here]

Views:
------
* **c2c_ytd_dpt** : return all invoiced lines before or equal to the current date (Year To Date), for each department. With all project informations
* **c2c_budget_analytic** : return the yearly financial budget and all budget line from current date

Functions:
----------
**c2c_xrate_conversion :**

* *input* : source currency ; destination currency ; source amount ; date taken in count to calculate the exchange rate
* *output* : calculated exchange rate ; calculated amount in destination currency
    
""",
    'author' : 'Camptocamp',
    'website' : 'http://www.camptocamp.com',
    'depends' : ['budget','hr_timesheet','analytic_department'],
    'data' : [
             ],
    'installable' : True,
    'active' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
