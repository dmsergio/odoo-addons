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

    operator_product_id = fields.Many2one(
        comodel_name="product.template",
        string="Operario")

    type_working_day = fields.Selection(
        [("regular", "Normal"),
         ("night", "Nocturna"),
         ("holiday", "Festiva"),
         ("night_holiday", "Nocturna/Festiva")],
        string="Tipo de jornada",
        default="regular")
