# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import datetime


class ImputeToSaleWiz(models.TransientModel):

    _name = 'impute.to_sale.wiz'

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Pedido de venta",
        domain="[('state', '!=', 'cancel'),"
               "('invoice_status', '!=', 'invoiced')]",
        required=True)

    sale_order_line_ids = fields.Many2many(
        comodel_name="sale.order.line",
        string="Líneas del pedido")

    product_id = fields.Many2one(
        comodel_name="product.template",
        string="Producto",
        help="Especifique el producto, ya sea de OPERARIOS o de LABORES, al "
             "que se utilizará para realizar la imputación del precio.",
        required=True)

    type_working_day = fields.Selection(
        [("regular", "Normal"),
         ("night", "Nocturna"),
         ("holiday", "Festiva"),
         ("night_holiday", "Nocturna/Festiva")],
        string="Tipo de jornada",
        default="regular")

    vip_customer = fields.Boolean(string="Cliente VIP?")

    quantity = fields.Float(
        string="Cantidad")

    order_date = fields.Date(
        string="Fecha",
        default=datetime.datetime.now().date())

    partner_id = fields.Many2one(comodel_name="res.partner",
                                   string="Cliente",
                                   readonly=True)

    def create_impute_to_sale(self):
        order_id = self.sale_id
        product_id = self.product_id.product_variant_id
        product_uom = product_id.uom_id
        product_uom_qty = self.quantity
        order_date = self.order_date
        price_unit = self.get_price_unit(product_id)
        self.env["sale.order.line"].create({
            "order_id": order_id.id,
            "product_id": product_id.id,
            "product_uom": product_uom.id or False,
            "product_uom_qty": product_uom_qty,
            "price_unit": price_unit,
            "order_date": order_date})
        context = self.env.context.copy()
        context["default_sale_id"] = self.sale_id.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'impute.to_sale.wiz',
            'context': context,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new'}

    @api.onchange('product_id')
    def onchange_product_id(self):
        """
        Onchange para agregar un domain al product_id y así poder filtrar por
        los productos que tienes su categoría interna LABORES y el propip
        producto del empleado.
        :return: dict
        """
        operator_category_ids = self.get_operator_category()
        machine_category_ids = self.get_machine_category()
        categories = operator_category_ids + machine_category_ids
        product_ids = self.env["product.template"].search([
            ("categ_id", "in", categories)])
        return {
            "domain": {
                "product_id": [("id", "in", product_ids.ids)]}}

    def get_price_unit(self, product_id):
        parent_operator_category_id = self.get_parent_operator_category()
        if product_id.categ_id.parent_id.id == parent_operator_category_id:
            if not self.sale_id.partner_id:
                if self.type_working_day == 'regular':
                    price = product_id.list_price
                elif self.type_working_day == 'night':
                    price = product_id.regular_night_price
                elif self.type_working_day == 'holiday':
                    price = product_id.regular_holiday_price
                else:
                    price = product_id.regular_night_holiday_price
            else:
                if self.type_working_day == 'regular':
                    price = product_id.vip_price
                elif self.type_working_day == 'night':
                    price = product_id.vip_night_price
                elif self.type_working_day == 'holiday':
                    price = product_id.vip_holiday_price
                else:
                    price = product_id.vip_night_holiday_price
        else:
            price = product_id.vip_price if self.sale_id.partner_id else \
                product_id.list_price
        return price

    def get_machine_category(self):
        return self.env["product.category"].browse(770).ids

    def get_parent_operator_category(self):
        return self.env["product.category"].browse(769).id

    def get_operator_category(self):
        parent_category_id = self.get_parent_operator_category()
        return self.env["product.category"].search([
            ("parent_id", "=", parent_category_id)]).ids

    @api.onchange('sale_id')
    def onchange_sale_id(self):
        if self.sale_id:
            self.vip_customer = self.sale_id.partner_id.partner_vip
            self.partner_id = self.sale_id.partner_id.id
            self.sale_order_line_ids = [(6, 0, self.sale_id.order_line.ids)]
        return



