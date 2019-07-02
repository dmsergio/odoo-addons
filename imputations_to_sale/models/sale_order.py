# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    global_price = fields.Float(string="Precio Global")

    @api.model
    def create(self, values):
        sale_id = super(SaleOrder, self).create(values)
        self._prepare_compensator_order_line(sale_id)
        for order_line_id in sale_id.order_line:
            order_line_id.recalculate_subtotal()
        return sale_id

    @api.one
    def write(self, values):
        res = super(SaleOrder, self).write(values)
        sale_id = self
        self._prepare_compensator_order_line(sale_id)
        for order_line_id in self.order_line:
            order_line_id.recalculate_subtotal()
        return res

    def _prepare_compensator_order_line(self, sale_id):
        sale_id.ensure_one()
        product_id = \
            self.env.ref("imputations_to_sale.product_template_0000_00_0000")
        product_id = product_id.product_variant_id
        if sale_id.order_line and sale_id.global_price:
            if product_id.id in sale_id.order_line.mapped("product_id").ids:
                line_ids = sale_id.order_line.filtered(
                    lambda x: x.product_id.id != product_id.id)
                total_amount = sum(line_ids.mapped("price_subtotal"))
                amount_compensator = \
                    sale_id.global_price - total_amount
                line_id = sale_id.order_line.filtered(
                    lambda x: x.product_id.id == product_id.id)
                line_id.write({"price_unit": amount_compensator})
            else:
                amount_compensator = \
                    sale_id.global_price - sale_id.amount_untaxed
                values = {
                    'order_id': sale_id.id,
                    'product_id': product_id.id,
                    'price_unit': amount_compensator,
                    'product_uom': product_id.uom_id.id,
                    'product_uom_qty': 1,
                    'name': product_id.name}
                self.env['sale.order.line'].create(values)
        return True
