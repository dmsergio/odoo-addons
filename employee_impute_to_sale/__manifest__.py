# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Arthor Sergio Díaz (<sdimar@yahoo.es>).
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
    "name": "Employee Impute To Sales",
    "version": "10.0.0.0.1",
    "author": "Sergio Díaz",
    "category": "Human Resources",
    "website": "",
    "summary": "Impute employee costs to sale orders",
    "depends": [
        "product"
    ],
    "data": [
        'views/product_template_view.xml',
    ],
    "active": False,
    "installable": True,
}
