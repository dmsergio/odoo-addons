# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


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
