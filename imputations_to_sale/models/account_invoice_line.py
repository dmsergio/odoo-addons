# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models, fields, _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    invoice_line_plant_hours = fields.Boolean(
        string="Horas en planta",
        compute='_compute_invoice_line_plant_hours')

    @api.model
    def create(self, values):
        invoice_line = super(AccountInvoiceLine, self).create(values)
        if invoice_line.partner_id.partner_plant_hours:
            invoice_line.invoice_line_plant_hours = \
                invoice_line.partner_id.partner_plant_hours
        return invoice_line

    @api.one
    def _compute_invoice_line_plant_hours(self):
        self.invoice_line_plant_hours = \
            self.sale_line_ids.sale_line_plant_hours
