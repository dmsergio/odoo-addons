# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    stock_qty = fields.Float(
        string="Stock",
        help="Unidades reales en stock.",
        compute="_compute_stock_qty")

    product_list_price_rel = fields.Float(
        string="Precio de venta",
        related="product_id.list_price",
        readonly=True)

    delivery_cost = fields.Float(
        string="Portes")

    @api.one
    def _compute_stock_qty(self):
        stock_quant_obj = self.env["stock.quant"]
        location_id = self.env.ref("stock.stock_location_stock")
        self.stock_qty = sum(stock_quant_obj.search([
            ("product_id", "=", self.product_id.id),
            ("location_id", "=", location_id.id)]).mapped("qty"))
