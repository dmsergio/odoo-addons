# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import UserError


class ImputeHoursWiz(models.TransientModel):

    _name = 'impute.material.wiz'

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

    quantity = fields.Float(
        string="Cantidad")

    order_date = fields.Date(
        string="Fecha")

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente",
        readonly=True)

    s_title = fields.Char(string="Title", readonly=True)

    def create_impute_to_sale(self):
        order_id = self.sale_id
        product_id = self.product_id.product_variant_id
        product_uom = product_id.uom_id
        product_uom_qty = self.quantity
        order_date = self.order_date
        price_unit = product_id.list_price
        if product_id.id in order_id.order_line.mapped("product_id").ids:
            line_id = order_id.order_line.filtered(
                lambda x: x.product_id.id == product_id.id)
            line_id.product_uom_qty += product_uom_qty
        else:
            self.env["sale.order.line"].create({
                "order_id": order_id.id,
                "product_id": product_id.id,
                "product_uom": product_uom.id or False,
                "product_uom_qty": product_uom_qty,
                "price_unit": price_unit,
                "order_date": order_date})
        for order_line_id in order_id.order_line:
            order_line_id.recalculate_subtotal()
        self.env["sale.order"]._prepare_compensator_order_line(order_id)
        context = self.env.context.copy()
        context["default_sale_id"] = self.sale_id.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'impute.material.wiz',
            'context': context,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'inline'}

    @api.onchange('product_id')
    def onchange_product_id(self):
        """
        Onchange para agregar un domain al product_id y así poder filtrar por
        los productos que sean de typo almacenables
        :return: dict
        """
        product_ids = self.env["product.template"].search([
            ("type", "=", "product")])
        return {
            "domain": {
                "product_id": [("id", "in", product_ids.ids)]}}

    @api.onchange('sale_id')
    def onchange_sale_id(self):
        if self.sale_id:
            self.partner_id = self.sale_id.partner_id.id
            self.s_title = self.sale_id.s_title
            line_ids = self.sale_id.order_line.filtered(
                lambda x: x.product_id.type == "product")
            self.sale_order_line_ids = [(6, 0, line_ids.ids)]
        return
