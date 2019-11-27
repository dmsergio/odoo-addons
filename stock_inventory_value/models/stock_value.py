# -*- encoding: utf-8 -*-
# Copyright 2019 Sergio Díaz  <sdimar@yahoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _
import logging

_logger = logging.getLogger(__name__)


class StockValue(models.Model):
    _name = 'stock.value'

    date = fields.Datetime(string="Date", required=True, readonly=True)
    stock_value = fields.Float(
        string="Stock value", required=True, readonly=True)

    @api.model
    def _stock_value_process(self):
        _logger.info("@Stock value cron: Start process")
        products = self.env['product.product'].search([
            ('type', 'in', ['consu', 'product'])])
        stock_value = 0
        for product in products:
            _logger.info("@Stock value cron: Computing total value for the "
                         "product [%s]" % product.name)
            stock_value += product.qty_available * product.standard_price
        _logger.info("@Stock value cron: Creating stock.value entry...")
        self.create({
            'date': fields.Datetime.now(),
            'stock_value': stock_value})
        _logger.info("@Stock value cron: End process.")
        return
