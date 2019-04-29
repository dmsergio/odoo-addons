# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    product_id = fields.Many2one(
        comodel_name="product.template",
        string="Producto relacionado")

    def launch_impute_sale_wiz(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Registrar líneas de Gasto",
            "res_model": "impute.to_sale.wiz",
            "view_mode": "form",
            "target": "new"}

    @api.onchange('product_id')
    def onchange_product_id(self):
        """
        Onchange para agregar un domain al product_id y así poder filtrar por
        los productos que su categoría padre es OPERARIOS.
        :return: dict
        """
        operator_categ_id = 769
        category_ids = self.env["product.category"].search([
            ("parent_id", "=", operator_categ_id)])
        product_ids = self.env["product.template"].search([
            ("categ_id", "in", category_ids.ids)])
        return {
            "domain": {
                "product_id": [("id", "in", product_ids.ids)]}}