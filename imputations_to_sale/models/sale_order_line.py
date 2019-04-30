# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields
import datetime


class SaleOrder(models.Model):

    _inherit = 'sale.order.line'

    order_date = fields.Date(
        string="Fecha",
        default=datetime.datetime.now().date())
