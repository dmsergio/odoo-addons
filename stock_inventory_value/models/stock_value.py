# -*- encoding: utf-8 -*-
# Copyright 2019 Sergio Díaz  <sdimar@yahoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class StockValue(models.Model):
    _name = 'stock.value'

    date = fields.Datetime(string="Date", required=True, readonly=True)
    stock_value = fields.Monetary(string="Stock value", required=True, readonly=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id.id)
    stock_value_line_ids = fields.One2many(comodel_name="stock.value.line", inverse_name="stock_value_id", string="Líneas", required=False, )


class StockValueLine(models.Model):
    _name = 'stock.value.line'

    date = fields.Date(string="Date", required=True, readonly=True)
    stock_value = fields.Monetary(string="Stock value", required=True, readonly=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id.id)
    product_id = fields.Many2one(comodel_name="product.template", string="Name", required=False, readonly=True, )
    stock_value_id = fields.Many2one(comodel_name="stock.value", string="Stock Value Id", required=False, readonly=True, ondelete='cascade',)

    @api.model
    def _stock_value_line_process(self):
        _logger.info("@Stock value cron: Start process")

        # Se crea primero la cabecera del stock value
        stock_value_obj = self.env['stock.value']
        stock_value_id = stock_value_obj.create({'date': fields.Datetime.now(), 'stock_value': 0.0, })
        print(stock_value_id)

        quant_obj = self.env['stock.quant']
        product_domain = [('type', '=', 'product'), ('excluded_product', '!=', True), ('qty_available', '>', 0.0), ('active', '=', True)]
        products = self.env['product.template'].search(product_domain)
        cont = 0
        for product in products:
            cont += 1
            _logger.info("@Stock value cron: Computing total value for the "
                         "product [%s]. Product %s of %s." % (product.name, cont, len(products)))
            quant_domain = [('product_id', '=', product.id), ('location_id.usage', '=', 'internal')]
            quants = quant_obj.search(quant_domain)
            stock_value = sum(quants.mapped('inventory_value'))
            # _logger.info("@Stock value cron: Creating stock.value entry...")
            self.create({'date': fields.Date.today(),
                         'stock_value': stock_value,
                         'product_id': product.id,
                         'stock_value_id': stock_value_id.id,
                         })
            # _logger.info("@Stock value cron: End process.")
        return