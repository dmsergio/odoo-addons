# -*- encoding: utf-8 -*-
# Copyright 2019 Sergio Díaz  <sdimar@yahoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _
import logging

_logger = logging.getLogger(__name__)


class StockValue(models.Model):
    _name = 'stock.value'

    date = fields.Datetime(string="Date", required=True, readonly=True)
    stock_value = fields.Monetary(
        string="Stock value", required=True, readonly=True,
        currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.user.company_id.currency_id.id)

    @api.model
    def _stock_value_process(self):
        _logger.info("@Stock value cron: Start process")
        quant_obj = self.env['stock.quant']
        product_domain = [('type', '=', 'product'),
                          ('excluded_product', '!=', True)]
        products = self.env['product.product'].search(product_domain)
        cont = 0
        stock_value = 0
        for product in products:
            cont += 1
            _logger.info("@Stock value cron: Computing total value for the "
                         "product [%s]. Product %s of %s." % (
                product.name, cont, len(products)))
            quant_domain = [
                ('product_id', '=', product.id),
                ('location_id.usage', '=', 'internal')]
            quants = quant_obj.search(quant_domain)
            stock_value += sum(quants.mapped('inventory_value'))
        _logger.info("@Stock value cron: Creating stock.value entry...")
        self.create({
            'date': fields.Datetime.now(),
            'stock_value': stock_value})
        _logger.info("@Stock value cron: End process.")
        return
