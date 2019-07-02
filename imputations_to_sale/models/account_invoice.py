# -*- coding: utf-8 -*-
from odoo import api, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

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
