# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import UserError


class CurrentValues():

    sale_id = False
    product_id = False


class ImputeHoursWiz(models.TransientModel):

    _name = 'impute.hours.wiz'

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente",
        readonly=True)

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Pedido de venta",
        domain="[('state', '!=', 'cancel'),"
               "('invoice_status', '!=', 'invoiced')]")

    product_id = fields.Many2one(
        comodel_name="product.template",
        string="Operario",
        help="Producto operario sobre el que se realizará el registro de "
             "tiempos, teniendo en cuenta cada uno de los registros en los "
             "puestos de trabajo indicados.")

    type_working_day = fields.Selection(
        [("regular", "Normal"),
         ("night", "Nocturna"),
         ("holiday", "Festiva"),
         ("night_holiday", "Nocturna/Festiva")],
        string="Tipo de jornada",
        default="regular")

    title = fields.Char(
        string="Título",
        readonly=True)

    vip_customer = fields.Boolean(
        string="Cliente VIP?",
        readonly=True)

    order_date = fields.Date(
        string="Fecha",
        default=datetime.datetime.now().date())

    total_hours = fields.Float(
        string="Total de horas",
        help="Total de horas registradas en el pedido de venta seleccionado.",
        readonly=True)

    subtotal = fields.Float(
        string="Subtotal",
        help="Subtotal calculado teniendo en cuenta el registro de tiempos del "
             "pedido de venta seleccionado.",
        readonly=True)

    work_order_quantity_ids = fields.One2many(
        comodel_name="work_order.quantity.wiz",
        inverse_name="impute_hours_id",
        string="Tiempos en Puesto de Trabajo",
        help="Indica la cantidad de horas a registrar del operario en los "
             "correspondientes puestos de trabajo.")

    sale_order_line_ids = fields.Many2many(
        comodel_name="sale.order.line",
        string="Tiempos del operario",
        help="Líneas del pedido de venta seleccionado con el registro de "
             "tiempos.",
        readonly=True)

    has_work_order_quantity_ids = fields.Boolean()

    @api.multi
    def create_impute_to_sale(self):
        if not self.work_order_quantity_ids:
            raise UserError(_(
                "Por favor, indica los tiempos a registrar de los puestos de "
                "trabajo. Gracias."))
        manual_product_id = self.env.ref("imputations_to_sale.manual_product")
        # creación de las líneas del pedido de venta de los puestos de trabajo
        for work_order_quantity_id in self.work_order_quantity_ids:
            if work_order_quantity_id.product_id.id != manual_product_id.id:
                product_id = work_order_quantity_id.product_id
                product_qty = work_order_quantity_id.product_qty
                price_unit = self.get_price_unit(product_id)
                self.create_sale_order_line(product_id, product_qty, price_unit)
        # creación de la línea correspondiente al producto operario
        product_id = CurrentValues.product_id
        product_qty = sum(self.work_order_quantity_ids.mapped("product_qty"))
        price_unit = self.get_price_unit(product_id)
        self.create_sale_order_line(product_id, product_qty, price_unit)
        context = self.env.context.copy()
        context["default_product_id"] = CurrentValues.product_id.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "impute.hours.wiz",
            "context": context,
            "view_type": "form",
            "view_mode": "form",
            "target": "inline"}

    def create_sale_order_line(self, product_id, product_qty, price_unit):
        line_values = {
            "order_id": CurrentValues.sale_id.id,
            "product_id": product_id.id,
            # "operator_product_id": CurrentValues.product_id.id,
            "product_uom": product_id.uom_id.id,
            "product_uom_qty": product_qty,
            "type_working_day": self.type_working_day,
            "price_unit": price_unit,
            "order_date": self.order_date}
        self.env["sale.order.line"].create(line_values)
        self.env.cr.commit()

    def get_price_unit(self, product_id):
        parent_operator_category_id = self.get_parent_operator_category()
        sale_id = CurrentValues.sale_id
        if product_id.categ_id.parent_id.id == parent_operator_category_id:
            if not sale_id.partner_id.partner_vip:
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
            price = product_id.vip_price if sale_id.partner_id else \
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

    @api.onchange("product_id", "order_date")
    def onchange_and_date_product_id(self):
        operator_category_ids = self.get_operator_category()
        product_ids = self.env["product.template"].search([
            ("categ_id", "in", operator_category_ids)])
        res = {
            "domain": {
                "product_id": [("id", "in", product_ids.ids)]}}
        if self.product_id and self.order_date:
            CurrentValues.product_id = self.product_id
            sale_order_line_obj = self.env["sale.order.line"]
            line_ids = sale_order_line_obj.search([
                ("operator_product_id", "=", self.product_id.id),
                ("order_date", "=", self.order_date)])
            self.sale_order_line_ids = [(6, 0, line_ids.ids)]
            self.compute_hours_and_subtotal(line_ids)
            return res
        self.total_hours = False
        self.subtotal = False
        return res

    @api.onchange("sale_id")
    def onchange_sale_id(self):
        if self.sale_id:
            CurrentValues.sale_id = self.sale_id
            self.vip_customer = self.sale_id.partner_id.partner_vip
            self.partner_id = self.sale_id.partner_id.id
            self.title = self.sale_id.s_title
            return
        self.vip_customer = False
        self.partner_id = False
        self.title = False
        return

    def compute_hours_and_subtotal(self, line_ids):
        """
        Función para calcular el total de horas registradas y el subtotal del
        pedido de venta seleccionado.
        :param line_ids: sale.order.line().
        :return: None
        """
        self.total_hours = sum(line_ids.filtered(
            lambda x: x.product_id.id == self.product_id.id).mapped(
            "product_uom_qty"))
        self.subtotal = sum(line_ids.mapped("price_subtotal"))
        return

    @api.onchange("work_order_quantity_ids")
    def onchange_work_order_quantity_ids(self):
        if len(self.work_order_quantity_ids) > 0:
            self.has_work_order_quantity_ids = True
        else:
            self.has_work_order_quantity_ids = False


class WorkOrderQuantityWiz(models.TransientModel):

    _name = 'work_order.quantity.wiz'

    impute_hours_id = fields.Many2one(
        comodel_name="impute.hours.wiz")

    product_id = fields.Many2one(
        comodel_name="product.template",
        string="Puesto de trabajo",
        required=True)

    product_qty = fields.Float(
        string="Horas",
        required=True)

    product_uom_id = fields.Many2one(
        comodel_name="product.uom",
        string="Unidad de medida",
        readonly=True)

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
        machine_product_ids = self.get_machine_category()
        product_ids = self.env["product.template"].search([
            ("categ_id", "in", machine_product_ids)])
        return {
            "domain": {
                "product_id": [("id", "in", product_ids.ids)]}}

    def get_machine_category(self):
        return self.env["product.category"].browse(770).ids

