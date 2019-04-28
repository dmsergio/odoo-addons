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

    product_id = fields.Many2one(
        comodel_name="product.template",
        string="Producto",
        help="Especifique el producto, ya sea el producto relacionado con el "
             "empleado actual, o bien una máquina.",
        required=True)

    type_working_day = fields.Selection(
        [("regular", "Normal"),
         ("night", "Nocturna"),
         ("holiday", "Festiva"),
         ("night_holiday", "Nocturna/Festiva")],
        string="Tipo de jornada",
        default="regular")

    vip_customer = fields.Boolean(
        string="Cliente VIP?")

    quantity = fields.Float(
        string="Cantidad")

    order_date = fields.Date(
        string="Fecha",
        default=datetime.datetime.now().date())

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
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'impute.to_sale.wiz',
            'context': self.env.context,
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
        employee_product_id = self.get_employee_product()
        category_id = self.get_machines_category()
        product_ids = self.env["product.template"].search([
            ("categ_id", "=", category_id.id)])
        filter_products = product_ids.ids + employee_product_id
        return {
            "domain": {
                "product_id": [("id", "in", filter_products)]}}

    def get_price_unit(self, product_id):
        employee_product_id = self.get_employee_product()
        if product_id.id in employee_product_id:
            if not self.vip_customer:
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
            price = product_id.vip_price if self.vip_customer else \
                product_id.list_price
        return price

    def get_machines_category(self):
        return self.env["product.category"].browse(770)

    def get_employee_product(self):
        employee_id = self.env["hr.employee"].browse(self._context["active_id"])
        return employee_id.product_id.ids if employee_id.product_id else []
