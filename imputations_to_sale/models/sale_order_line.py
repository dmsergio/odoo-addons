# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
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

    def recalculate_subtotal(self):
        pricelist_obj = self.env["mejisa.product.pricelist"]
        pricelist_id = pricelist_obj.search([
            ("amount_1", "<=" , self.price_subtotal),
            ("amount_2", ">=" , self.price_subtotal)],limit=1)
        if pricelist_id:
            increase = pricelist_id.increase
            if self.order_id.partner_id.reduced_rate:
                increase -= pricelist_id.decrease
            self.price_subtotal += (self.price_subtotal * increase) / 100
        return
