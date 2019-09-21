from odoo import models, fields, api


class ProductSupplierinfo(models.Model):

    _inherit = 'product.supplierinfo'

    delivery_cost = fields.Float(
        string="Portes")
