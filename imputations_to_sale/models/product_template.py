# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    regular_night_price = fields.Float(
        string="Precio Nocturno")

    regular_holiday_price = fields.Float(
        string="Precio Festivo")

    regular_night_holiday_price = fields.Float(
        string="Precio Nocturno/Festivo")

    vip_price = fields.Float(
        string="Precio VIP")

    vip_night_price = fields.Float(
        string="Precio Nocturno VIP")

    vip_holiday_price = fields.Float(
        string="Precio Festivo VIP")

    vip_night_holiday_price = fields.Float(
        string="Precio Nocturno/Festivo VIP")
    categ_labors = fields.Boolean(string="Labores", compute='_compute_categ_id')
    categ_operators = fields.Boolean(string="Operarios", compute='_compute_categ_id')

    @api.one
    @api.depends('categ_id')
    def _compute_categ_id(self):
        """ Este método muestra la pestaña Precios de venta en función del
            del tipo de categoria selseccionado por el usuario"""
        categ_obj = self.env['product.category']
        categ_id = categ_obj.search([('id', '=', self.categ_id.id)])
        if categ_id:
            id_labors = 770
            id_operators = 769
            if categ_id.id == id_labors:
                self.categ_labors = True
            elif categ_id.id == id_operators:
                self.categ_operators = True
            else:
                return False