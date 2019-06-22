# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class SaleOrder(models.Model):

    _inherit = 'sale.order'


    global_price = fields.Float(string="Precio Global")

    global_price_stored = fields.Float(string="Precio Global stored",
                                compute="_prepare_compensator_order_line")

    @api.multi
    @api.depends('order_line')
    def _prepare_compensator_order_line(self):
        self.ensure_one()
        order_line_ids= []
        product_id = \
            self.env.ref("imputations_to_sale."
                         "product_template_000_00_0000")
        order_id = self.id
        if self.order_line and self.global_price:
            order_line_ids = [i for i in self.order_line]
            compnesator = self.global_price - self.amount_total
            vals = {
                'order_id': order_id,
                'product_id': product_id.id,
                'price_unit': compnesator,
                'product_uom': product_id.uom_id.id,
                'product_uom_qty': 1,
                'name': product_id.name
            }
            line_id = self.env['sale.order.line'].create(vals)
            order_line_ids.append(line_id)

        #self.order_line = [(6, 0, order_line_ids)]
        return True
