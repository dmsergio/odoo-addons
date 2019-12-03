# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_ids = fields.Many2many(
        comodel_name="sale.order",
        relation="sale_order_invoice_rel",
        column1="invoice_order_id",
        column2="sale_order_id",
        string='Sale Orders',
        readonly=True,
        compute="_get_sale_order_from_invoice_line",
        help="Estos son todos los pedidos relacionados a la factura.")

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        if res and self.type == "in_invoice":
            self.set_product_cost()
        return res

    def set_product_cost(self):
        """
        Función para establecer el precio de coste a los productos de la
        factura de compra.
        :return: None
        """
        # OPERARIOS
        operator_category_ids = self.get_operator_category()
        operator_product_ids = self.env["product.template"].search([
            ("categ_id", "in", operator_category_ids)]).mapped(
            "product_variant_id")

        # PUESTO DE TRABAJO
        machine_product_ids = self.get_machine_category()
        machine_product_ids = self.env["product.template"].search([
            ("categ_id", "in", machine_product_ids)]).mapped(
            "product_variant_id")

        product_ids = operator_product_ids.ids + machine_product_ids.ids
        line_ids = self.invoice_line_ids.filtered(
            lambda x: x.product_id.id not in product_ids)

        for line_id in line_ids:
            line_id.product_id.write({"standard_price": line_id.price_unit})
        return

    def get_parent_operator_category(self):
        return self.env["product.category"].browse(769).id

    def get_operator_category(self):
        parent_category_id = self.get_parent_operator_category()
        return self.env["product.category"].search([
            ("parent_id", "=", parent_category_id)]).ids

    def get_machine_category(self):
        return self.env["product.category"].browse(770).ids


    @api.multi
    @api.depends('origin')
    def _get_sale_order_from_invoice_line(self):
        sale_obj = self.env['sale.order']
        sale_ids = sale_obj
        if self.origin:
            for recs in self.invoice_line_ids:
                order_id = sale_obj.get_sale_order(recs.sale_line_ids)
                if order_id: sale_ids |= order_id
            if sale_ids:
                self.sale_ids = [(6, 0, sale_ids.ids)]
        return True
