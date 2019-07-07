# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import datetime


class SaleOrder(models.Model):

    _inherit = 'sale.order.line'

    order_date = fields.Date(
        string="Fecha",
        default=datetime.datetime.now().date())

    operator_product_id = fields.Many2one(
        comodel_name="product.template",
        string="Operario")

    type_working_day = fields.Selection(
        [("regular", "Normal"),
         ("night", "Nocturna"),
         ("holiday", "Festiva"),
         ("night_holiday", "Nocturna/Festiva")],
        string="Tipo de jornada",
        default="regular")

    def recalculate_subtotal(self):
        # OPERARIOS
        operator_category_ids = self.get_operator_category()
        operator_product_ids = self.env["product.template"].search([
            ("categ_id", "in", operator_category_ids)]).mapped(
            "product_variant_id")

        # PUESTO DE TRABAJO
        machine_product_ids = self.get_machine_category()
        machine_product_ids = self.env["product.template"].search([
            ("categ_id", "in", machine_product_ids)]).mapped(
            "product_variant_id")

        product_ids = operator_product_ids.ids + machine_product_ids.ids
        product_ids.append(self.env.ref(
            "imputations_to_sale.product_template_0000_00_0000").\
                           product_variant_id.id)

        if self.product_id.id not in product_ids:
            subtotal = self.purchase_price * self.product_uom_qty
            pricelist_obj = self.env["mejisa.product.pricelist"]
            pricelist_id = pricelist_obj.search([
                ("amount_1", "<=" , subtotal),
                ("amount_2", ">=" , subtotal)],limit=1)
            if pricelist_id:
                increase = pricelist_id.increase
                increase -= pricelist_id.decrease if \
                    self.order_id.partner_id.reduced_rate else 0
                self.price_subtotal = subtotal + (subtotal * increase) / 100
                self.price_total = self.price_subtotal + (
                        self.price_subtotal * self.tax_id.amount) / 100
        return

    def get_parent_operator_category(self):
        return self.env["product.category"].browse(769).id

    def get_operator_category(self):
        parent_category_id = self.get_parent_operator_category()
        return self.env["product.category"].search([
            ("parent_id", "=", parent_category_id)]).ids

    def get_machine_category(self):
        return self.env["product.category"].browse(770).ids