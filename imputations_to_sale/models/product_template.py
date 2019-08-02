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

    categ_labors = fields.Boolean(
        string="Labores",
        compute='_compute_operators_categ_id')

    categ_operators = fields.Boolean(
        string="Operarios",
        compute='_compute_operators_categ_id')

    fixed_price = fields.Boolean(string="Precio fijo")


    @api.one
    @api.depends('categ_id')
    def _compute_operators_categ_id(self):
        """ Este método muestra la pestaña Precios de venta en función del
            del tipo de categoria selseccionado por el usuario"""
        machine_category_ids = self.get_machine_category()
        categ_obj = self.env['product.category']
        parent_category_id = categ_obj.browse(769).id
        category_ids = categ_obj.search([
            ("parent_id", "=", parent_category_id)]).ids
        if self.categ_id.id in category_ids or \
                self.categ_id.id == parent_category_id:
            self.categ_operators = True
        elif self.categ_id.id in machine_category_ids:
            self.categ_labors = True
        else:
            return False

    def get_machine_category(self):
        return self.env["product.category"].browse(770).ids

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|',
                      ('name', operator, name),
                      ('default_code', operator, name)]
        product_ids = self.search(domain + args, limit=limit)
        return product_ids.name_get()
