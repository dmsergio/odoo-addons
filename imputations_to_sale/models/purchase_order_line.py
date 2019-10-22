# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    no_act = fields.Boolean(
        string="No act",
        help="No actualizar el precio de coste en la ficha del producto.")

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

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line_id in self:
            price_unit = line_id.price_unit
            product_qty = line_id.product_qty
            discount = line_id.discount
            price_subtotal = (price_unit * product_qty * (1 - discount / 100))
            # Comprobamos el tipo de impuesto
            if line_id.taxes_id.amount_type == 'group':
                taxes_amount = sum(
                    line_id.taxes_id.children_tax_ids.mapped("amount")) / 100
            else:
                taxes_amount = sum(line_id.taxes_id.mapped("amount")) / 100
            price_total = price_subtotal + (price_subtotal * taxes_amount)
            line_id.update({
                "price_subtotal": price_subtotal,
                "price_total": price_total,
                "price_tax": price_total - price_subtotal})
            line_id.price_subtotal = price_subtotal
            line_id.price_total = price_total
            line_id.price_tax = price_total - price_subtotal

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        """
        Check if a discount is defined into the supplier info and if so then
        apply it to the current purchase order line
        """
        res = super(PurchaseOrderLine, self)._onchange_quantity()
        if self.product_id:
            date = None
            if self.order_id.date_order:
                date = fields.Date.to_string(fields.Date.from_string(
                    self.order_id.date_order))
            product_supplierinfo = self.product_id._select_seller(
                partner_id=self.partner_id, quantity=self.product_qty,
                date=date, uom_id=self.product_uom)
            if product_supplierinfo:
                self.delivery_cost = product_supplierinfo.delivery_cost
        return res
