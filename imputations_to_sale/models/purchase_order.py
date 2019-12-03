# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    def _amount_all(self):
        self.update({
            "amount_tax": sum(self.order_line.mapped("price_tax")),
            "amount_untaxed": sum(self.order_line.mapped("price_subtotal")),
            "amount_total": sum(self.order_line.mapped("price_total"))})

    @api.model
    def create(self, values):
        sale = super(PurchaseOrder, self).create(values)
        sale.add_partner_in_product_supplierinfo()
        return sale

    @api.multi
    def write(self, values):
        res = super(PurchaseOrder, self).write(values)
        if res:
            for sale in self:
                sale.add_partner_in_product_supplierinfo()
        return res


    def add_partner_in_product_supplierinfo(self):
        """
        This method add a new supplier in the product file every time a purchase
        is made with a different supplier.
        """
        self.ensure_one()
        product_supplier_info_obj = self.env['product.supplierinfo']
        for line in self.order_line:
            sellers = line.product_id.seller_ids
            supplier = \
                sellers.filtered(lambda x: x.name.id == self.partner_id.id)
            if not supplier:
                new_supplier = product_supplier_info_obj.create({
                    'name': self.partner_id.id})
                line.product_id.seller_ids = [(4, new_supplier.id)]
        return

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        if res:
            self.update_product_supplier_cost()
        return res


    def update_product_supplier_cost(self):
        """
        Method to update costs on supplier of products of each purchase order
        line.
        """
        for line in self.order_line:
            supplier = line.product_id.seller_ids.filtered(
                lambda x: x.name.id == self.partner_id.id)
            if supplier:
                supplier.write({
                    'price': line.price_unit,
                    'discount': line.discount,
                    'delivery_cost': line.delivery_cost})
                if not line.no_act:
                    price = line.price_unit * (
                            1 - line.discount) + line.delivery_cost
                    line.product_id.write({'standard_price': price})
        return