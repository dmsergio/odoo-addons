# -*- encoding: utf-8 -*-
# Copyright 2019 Sergio Díaz  <sdimar@yahoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class StockValue(models.Model):
    _name = 'stock.value'

    date = fields.Datetime(string="Date", required=True, readonly=True)
    stock_value = fields.Float(
        string="Stock value", required=True, readonly=True)

    @api.model
    def _stock_value_process(self):
        # TODO
        print("_stock_value_process...")
        return
