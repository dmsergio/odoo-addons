# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
#   Jesus Pablo Ndong(<jesusndong@jesusndong.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class MejisaProductPricelist(models.Model):
    _name = 'mejisa.product.pricelist'


    amount_1 = fields.Float(string="Importe-1")

    amount_2 = fields.Float(string="Importe-2")

    increase = fields.Integer(string="Aumento")
    decrease = fields.Integer(string="Disminución")