# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models, fields, _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    delivery_cost = fields.Float(
        string="Portes")

    @api.model
    def create(self, values):
        invoice_line_id = super(AccountInvoiceLine, self).create(values)
        if invoice_line_id.purchase_line_id:
            invoice_line_id.write({
                "delivery_cost":
                    invoice_line_id.purchase_line_id.delivery_cost})
        return invoice_line_id

    @api.one
    @api.depends(
        'price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id',
        'invoice_id.company_id', 'invoice_id.date_invoice', 'invoice_id.date',
        'delivery_cost')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(
                price, currency, self.quantity, product=self.product_id,
                partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes[
            'total_excluded'] + self.delivery_cost if taxes else \
            self.quantity * price + self.delivery_cost
        if self.invoice_id.currency_id and self.invoice_id.company_id and \
                self.invoice_id.currency_id != \
                self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(
                date=self.invoice_id._get_currency_rate_date()).compute(
                price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
