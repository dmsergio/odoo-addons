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

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'delivery_cost')
    def _compute_amount(self):
        for line_id in self:
            price_unit = line_id.price_unit
            product_qty = line_id.product_qty
            discount = line_id.discount
            delivery_cost = line_id.delivery_cost
            price_subtotal = \
                price_unit * product_qty - ((price_unit * product_qty) *
                                            (discount / 100)) + \
                delivery_cost
            price_total = \
                price_subtotal + (price_subtotal * sum(
                    line_id.taxes_id.mapped("amount")) / 100)
            line_id.update({
                "price_subtotal": price_subtotal,
                "price_total": price_total,
                "price_tax": price_total - price_subtotal})
            line_id.price_subtotal = price_subtotal
            line_id.price_total = price_total
            line_id.price_tax = price_total - price_subtotal
