# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ImputeHoursWiz(models.TransientModel):
    _name = 'impute.hours.wiz'

    partner_id = fields.Many2one(
        comodel_name='res.partner', string="Cliente", readonly=True,
        ondelete='cascade')
    sale_id = fields.Many2one(
        comodel_name='sale.order', string="Pedido de venta",
        domain="[('state', 'in', ('draft', 'sent')),"
               "('invoice_status', '!=', 'invoiced')]", ondelete='cascade')
    product_id = fields.Many2one(
        comodel_name='product.template', string="Operario",
        help="Producto operario sobre el que se realizará el registro de "
             "tiempos, teniendo en cuenta cada uno de los registros en los "
             "puestos de trabajo indicados.", ondelete='cascade')
    product_dummy_id = fields.Many2one(comodel_name='product.template')
    type_working_day = fields.Selection(
        [('regular', 'Normal'),
         ('night', 'Nocturna'),
         ('holiday', 'Festiva'),
         ('night_holiday', 'Nocturna/Festiva')], string="Tipo de jornada",
        default='regular')
    title = fields.Char(string="Título", readonly=True)
    vip_customer = fields.Boolean(string="Cliente VIP?", readonly=True)
    plant_hours = fields.Boolean(string="Horas en planta")
    order_date = fields.Date(string="Fecha", required=True)
    total_hours = fields.Float(
        string="Total de horas operario",
        help="Total de horas imputadas por el operario y fecha seleccionados.",
        readonly=True)
    sale_hours = fields.Float(
        string="Total de horas pedido",
        help="Total de horas imputadas del pedido de venta seleccionado.",
        compute='_compute_total_sale_hours', readonly=True)
    subtotal = fields.Float(
        string="Subtotal",
        help="Subtotal calculado teniendo en cuenta el registro de tiempos del "
             "operario y fecha indicados.", readonly=True)
    work_order_quantity_ids = fields.One2many(
        comodel_name='work_order.quantity.wiz', inverse_name='impute_hours_id',
        string="Tiempos en Puesto de Trabajo",
        help="Indica la cantidad de horas a registrar del operario en los "
             "correspondientes puestos de trabajo.", ondelete='cascade')
    sale_order_line_ids = fields.Many2many(
        comodel_name='sale.order.line', string="Tiempos del operario",
        help="Líneas del pedido de venta seleccionado con el registro de "
             "tiempos.", readonly=True, ondelete='cascade')
    has_work_order_quantity_ids = fields.Boolean(
        compute='_compute_has_work_order_quantity_ids')

    @api.multi
    @api.depends('product_id', 'sale_id', 'work_order_quantity_ids')
    def create_impute_to_sale(self):
        if not self.work_order_quantity_ids:
            raise UserError(_(
                "Por favor, indica los tiempos a registrar de los puestos de "
                "trabajo. Gracias."))

        # se busca el producto manual y el producto del operario
        manual_product = self.env.ref('imputations_to_sale.manual_product')
        operator_product = self.product_dummy_id

        # creación de las líneas del pedido de venta de los puestos de trabajo
        for work_order_qty in self.work_order_quantity_ids:
            if work_order_qty.product_id.id != manual_product.id:
                # se crea la línea para la máquina y el operario
                for product in (operator_product + work_order_qty.product_id):
                    product_qty = work_order_qty.product_qty
                    price_unit, cost_unit = self.get_price(product)
                    name = product.display_name
                    self.create_sale_order_line(
                        product, product_qty, price_unit, cost_unit, name)
            else:
                # se crea la línea solo para el operario
                product_qty = work_order_qty.product_qty
                price_unit, cost_unit = self.get_price(operator_product)
                name = "[%s] %s" % (operator_product.default_code or "",
                                    operator_product.name)
                self.create_sale_order_line(
                    operator_product, product_qty, price_unit, cost_unit,
                    name)
        # creación de la línea compensatoria
        self.sale_id._prepare_compensator_order_line(self.sale_id)
        # recalcular el subtotal en función de la tarifa
        self.sale_id.order_line.recalculate_subtotal()
        # preparar context y mostrar de nuevo el wizard
        context = self.env.context.copy()
        context.update({
            'default_product_id': operator_product.id,
            'default_order_date': self.order_date})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'impute.hours.wiz',
            'context': context,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'inline'}

    def create_sale_order_line(
            self, product_id, product_qty, price_unit, cost_unit, name):
        operator_product = self.product_dummy_id
        line_values = {
            'order_id': self.sale_id.id,
            'name': name,
            'product_id': product_id.product_variant_id.id,
            'operator_product_id': operator_product.id,
            'product_uom': product_id.product_variant_id.uom_id.id,
            'product_uom_qty': product_qty,
            'type_working_day': self.type_working_day,
            'price_unit': price_unit,
            'purchase_price': cost_unit,
            'order_date': self.order_date,
            'sale_line_plant_hours': self.plant_hours}
        self.env['sale.order.line'].create(line_values)

    def get_price(self, operator_product_id, product_id=False):
        """
        Función para obtener el precio unitario y de coste de la línea del
        presupuesto realizando la suma del precio de coste de la máquina y del
        operario.
        :param product_id (product.template): máquina.
        :param operator_product_id (product.template): operario.
        :return (float): price and cost
        """
        sale = self.sale_id
        if not sale.partner_id.partner_vip:
            if operator_product_id.categ_id.id != 770:
                if self.type_working_day == 'regular':
                    price = operator_product_id.list_price
                elif self.type_working_day == 'night':
                    price = operator_product_id.regular_night_price
                elif self.type_working_day == 'holiday':
                    price = operator_product_id.regular_holiday_price
                else:
                    price = operator_product_id.regular_night_holiday_price
            else:
                price = operator_product_id.list_price
        else:
            if operator_product_id.categ_id.id != 770:
                if self.type_working_day == 'regular':
                    price = operator_product_id.vip_price
                elif self.type_working_day == 'night':
                    price = operator_product_id.vip_night_price
                elif self.type_working_day == 'holiday':
                    price = operator_product_id.vip_holiday_price
                else:
                    price = operator_product_id.vip_night_holiday_price
            else:
                price = operator_product_id.vip_price
        if product_id:
            price += \
                product_id.list_price if not sale.partner_id.partner_vip \
                    else product_id.vip_price
            cost = \
                product_id.standard_price + operator_product_id.standard_price
            return price, cost
        return price, operator_product_id.standard_price

    def get_machine_category(self):
        return self.env['product.category'].browse(770).ids

    def get_parent_operator_category(self):
        return self.env['product.category'].browse(769).id

    def get_operator_category(self):
        parent_category_id = self.get_parent_operator_category()
        return self.env['product.category'].search([
            ('parent_id', '=', parent_category_id)]).ids

    @api.onchange('product_id', 'order_date')
    def onchange_date_and_product_id(self):
        self.product_dummy_id = self.product_id
        operator_category_ids = self.get_operator_category()
        products = self.env['product.template'].search([
            ('categ_id', 'in', operator_category_ids)])
        res = {
            'domain': {
                'product_id': [('id', 'in', products.ids)]}}
        if self.product_dummy_id and self.order_date:
            sale_order_line_obj = self.env['sale.order.line']
            lines = sale_order_line_obj.search([
                ('operator_product_id', '=', self.product_dummy_id.id),
                ('order_date', '=', self.order_date)])
            sorted_lines = lines.sorted(lambda l: int(l.order_id.id))
            self.sale_order_line_ids = [(6, 0, sorted_lines.ids)]
            self.compute_hours_and_subtotal(sorted_lines)
            return res
        self.total_hours = False
        self.subtotal = False
        return res

    @api.onchange('sale_id')
    def onchange_sale_id(self):
        if self.sale_id:
            self.vip_customer = self.sale_id.partner_id.partner_vip
            self.plant_hours = self.sale_id.partner_id.partner_plant_hours
            self.partner_id = self.sale_id.partner_id.id
            self.title = self.sale_id.s_title
            return
        self.sale_id = False
        self.vip_customer = False
        self.partner_id = False
        self.title = False
        return

    def compute_hours_and_subtotal(self, sale_lines):
        """
        Función para calcular el total de horas registradas y el subtotal del
        pedido de venta seleccionado.
        :param sale_lines: sale.order.line().
        :return: None
        """
        product = self.product_dummy_id.product_variant_id
        self.total_hours = sum(sale_lines.filtered(
            lambda x: x.product_id.id == product.id).mapped('product_uom_qty'))
        self.subtotal = sum(sale_lines.mapped('price_subtotal'))
        return

    @api.depends('sale_id')
    def _compute_total_sale_hours(self):
        """
        Esta función suma las horas invertidas en las líneas del pedido
        realacionado.
        :return:
        """
        if self.sale_id:
            sale_lines = self.sale_id.order_line
            if sale_lines:
                SaleLine = self.env['sale.order.line']
                operator_category_ids = SaleLine.get_operator_category()
                operator_product_ids = self.env["product.template"].search([
                    ("categ_id", "in", operator_category_ids)]).mapped(
                    "product_variant_id")
                sum_hours = sum(sale_lines.filtered(
                    lambda sl: sl.product_id.id in operator_product_ids.ids
                ).mapped('product_uom_qty'))
                self.sale_hours = sum_hours

    @api.depends('work_order_quantity_ids')
    def _compute_has_work_order_quantity_ids(self):
        for record in self:
            record.has_work_order_quantity_ids = bool(
                record.work_order_quantity_ids)


class WorkOrderQuantityWiz(models.TransientModel):
    _name = 'work_order.quantity.wiz'

    impute_hours_id = fields.Many2one(
        comodel_name='impute.hours.wiz', ondelete='cascade')
    product_id = fields.Many2one(
        comodel_name='product.template', string="Puesto de trabajo",
        required=True, ondelete='cascade')
    product_qty = fields.Float(string="Horas", required=True)
    product_uom_id = fields.Many2one(
        comodel_name='product.uom', string="Unidad de medida", readonly=True,
        ondelete='cascade')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
        machine_product_ids = self.get_machine_category()
        products = self.env['product.template'].search([
            ('categ_id', 'in', machine_product_ids)])
        return {
            'domain': {
                'product_id': [('id', 'in', products.ids)]}}

    def get_machine_category(self):
        return self.env['product.category'].browse(770).ids
