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
        sale_id = super(PurchaseOrder, self).create(values)
        self.add_partner_in_product_supplierinfo(
            sale_id.partner_id, sale_id.order_line)
        return sale_id

    @api.one
    def write(self, values):
        res = super(PurchaseOrder, self).write(values)
        self.add_partner_in_product_supplierinfo(self.partner_id, self.order_line)
        return res


    def add_partner_in_product_supplierinfo(self, partner_id, order_line):
        ''' This function add a new supplier in the product file every time a
            purchase is made with a different supplier
        :param partner_id:
        :param order_line:
        :return:
        '''
        obj_prodsupplierinfo = self.env['product.supplierinfo']
        if partner_id and order_line:
            for line in order_line:
                seller_ids = line.product_id.seller_ids
                supplierinfo = \
                    seller_ids.filtered(lambda x: x.name.id == partner_id.id)
                if not supplierinfo:
                    supplierinfo_vals = {
                        'name': partner_id.id
                    }
                    supplierinfo_id = \
                        obj_prodsupplierinfo.create(supplierinfo_vals)
                    line.product_id.seller_ids = [(4, supplierinfo_id.id)]
            return True

    @api.multi
    def button_confirm(self):
        super(PurchaseOrder, self).button_confirm()
        self.update_product_supplier_cost(self.partner_id, self.order_line)
        return True


    def update_product_supplier_cost(self, partner_id, order_line):
        ''' Update product supplier cost
        :param partner_id:
        :param order_line:
        :return:
        '''
        if partner_id and order_line:
            for line_id in order_line:
                seller_ids = line_id.product_id.seller_ids
                if seller_ids:
                    supplierinfo = \
                        seller_ids.filtered(
                            lambda x: x.name.id == partner_id.id)
                    if supplierinfo:
                        supplierinfo.write({
                            'price': line_id.price_unit,
                            'discount': line_id.discount,
                            'delivery_cost': line_id.delivery_cost})
                        if not line_id.no_act:
                            line_id.product_id.write(
                                {"standard_price": line_id.price_unit -
                                                   (line_id.price_unit *
                                                    (line_id.discount / 100)) +
                                                   line_id.delivery_cost})
