# -*- coding: utf-8 -*-
# © 2020 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class SaleOrderRemoveLines(models.TransientModel):

    _name = 'sale.order.remove_lines'

    def _get_default_mrp_bom_ids(self):
        sale = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        return sale.order_line.mapped('mrp_bom_id')

    mrp_bom_ids = fields.Many2many(
        comodel_name="mrp.bom",
        string="Lista de materiales",
        default=lambda self: self._get_default_mrp_bom_ids()
    )
    mrp_bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        required=True,
        string="Lista de materiales"
    )

    def remove_lines(self):
        sale = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        lines = sale.order_line.filtered(
            lambda l: l.mrp_bom_id == self.mrp_bom_id)
        lines.unlink()
        return True
