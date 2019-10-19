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
        """
        Muestra la pestaña Precios de venta en función del del tipo de
        categoria seleccionado por el usuario
        """
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
        return True

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

    def get_parent_operator_category(self):
        return self.env["product.category"].browse(769).id

    def get_operator_category(self):
        parent_category_id = self.get_parent_operator_category()
        return self.env["product.category"].search([
            ("parent_id", "=", parent_category_id)]).ids

    def recalculate_price_list(self, product_id):
        """
        Method to recalculate the product price list looking for in Mejisa
        pricelists.
        :param product_id (product.template): product to recalculate its price
        """
        if self.fixed_price:
            return
        # OPERATORS
        operator_category_ids = self.get_operator_category()
        operator_product_ids = self.env["product.template"].search([
            ("categ_id", "in", operator_category_ids)]).mapped(
            "product_variant_id")
        # WORKPLACES
        machine_product_ids = self.get_machine_category()
        machine_product_ids = self.env["product.template"].search([
            ("categ_id", "in", machine_product_ids)]).mapped(
            "product_variant_id")
        product_ids = operator_product_ids.ids + machine_product_ids.ids
        product_ids.append(
            self.env.ref("imputations_to_sale.product_template_0000_00_0000").
                product_variant_id.id)
        if product_id.product_variant_id.id not in product_ids:
            cost_price = product_id.standard_price
            pricelist_obj = self.env["mejisa.product.pricelist"]
            pricelist_id = pricelist_obj.search([
                ("amount_1", "<=", cost_price),
                ("amount_2", ">=", cost_price)], limit=1)
            if pricelist_id:
                increase = pricelist_id.increase
                list_price = cost_price + (cost_price * increase) / 100
                product_id.write({'list_price': list_price})

    @api.model
    def create(self, values):
        product_id = super(ProductTemplate, self).create(values)
        self.recalculate_price_list(product_id)
        return product_id

    @api.one
    def write(self, values):
        res = super(ProductTemplate, self).write(values)
        if res and not values.get("list_price", False):
            self.recalculate_price_list(self)
        return res

    @api.onchange("default_code")
    def onchange_default_code(self):
        if self.default_code and len(self.default_code) >= 4:
            category = self.env["product.category"].search([
                ("name", "like", "%s%%" % self.default_code[0:4])], limit=1)
            if category:
                self.categ_id = category.id


class ProductProduct(models.Model):

    _inherit = 'product.product'

    @api.model
    def create(self, values):
        product_id = super(ProductProduct, self).create(values)
        self.env["product.template"].recalculate_price_list(product_id)
        return product_id

    @api.one
    def write(self, values):
        res = super(ProductProduct, self).write(values)
        if res and not values.get("list_price", False):
            self.env["product.template"].recalculate_price_list(self)
        return res

    @api.onchange("default_code")
    def onchange_default_code(self):
        if self.default_code and len(self.default_code) >= 4:
            category = self.env["product.category"].search([
                ("name", "like", "%s%%" % self.default_code[0:4])], limit=1)
            if category:
                self.categ_id = category.id
