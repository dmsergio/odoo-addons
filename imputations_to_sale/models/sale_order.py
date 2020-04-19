# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    global_price = fields.Float(string="Precio Global")
    picking_pending = fields.Boolean(
        string="Pedidos pendientes",
        states={
            'draft': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)]})
    mrp_bom_ids = fields.Many2many(
        comodel_name='mrp.bom',
        string='Lista de materiales'
        # compute='_compute_mrp_bom_lines'
    )

    @api.model
    def create(self, values):
        sale_id = super(SaleOrder, self).create(values)
        self.explode_bom()
        sale_id.order_line.recalculate_subtotal()
        self._prepare_compensator_order_line(sale_id)
        return sale_id

    @api.one
    def write(self, values):
        res = super(SaleOrder, self).write(values)
        self.explode_bom()
        if not self.state == "done":
            sale_id = self
            self.order_line.recalculate_subtotal()
            self._prepare_compensator_order_line(sale_id)
        return res

    def _prepare_compensator_order_line(self, sale_id):
        sale_id.ensure_one()
        product_id = \
            self.env.ref("imputations_to_sale.product_template_0000_00_0000")
        product_id = product_id.product_variant_id
        if sale_id.global_price:
            if product_id.id in sale_id.order_line.mapped("product_id").ids:
                line_ids = sale_id.order_line.filtered(
                    lambda x: x.product_id.id != product_id.id)
                total_amount = sum(line_ids.mapped("price_subtotal"))
                amount_compensator = \
                    sale_id.global_price - total_amount
                line_id = sale_id.order_line.filtered(
                    lambda x: x.product_id.id == product_id.id)
                line_id.write({"price_unit": amount_compensator})
            else:
                amount_compensator = \
                    sale_id.global_price - sale_id.amount_untaxed
                values = {
                    'order_id': sale_id.id,
                    'product_id': product_id.id,
                    'price_unit': amount_compensator,
                    'product_uom': product_id.uom_id.id,
                    'product_uom_qty': 1,
                    'name': product_id.name}
                self.env['sale.order.line'].create(values)
        elif sale_id.order_line and sale_id.global_price == 0:
            if product_id.id in sale_id.order_line.mapped("product_id").ids:
                line_id = sale_id.order_line.filtered(
                    lambda x: x.product_id.id == product_id.id)
                line_id.unlink()
        return True


    def get_sale_order(self, lines):
        order_id = False
        if lines:
            order_id = lines.filtered(lambda x: x.order_id)
            order_id = self.search([('id', '=', order_id.order_id.id)], limit=1)
            return order_id

    def explode_bom(self):
        sale_line_obj = self.env["sale.order.line"]
        for line in self.order_line:
            boms = line.product_id.bom_ids.filtered(
                    lambda x: x.type == 'normal')
            if not boms:
                continue
            bom = max(boms, key=lambda x: x['id'])
            for bom_line in bom.bom_line_ids:
                sale_line_obj.create({
                    'product_id': bom_line.product_id.id,
                    'product_uom_qty': bom_line.product_qty *
                                       line.product_uom_qty,
                    'price_unit': bom_line.product_id.lst_price,
                    'mrp_bom_id': bom_line.id,
                    'purchase_price': bom_line.product_id.standard_price,
                    'name': '[%s] %s' % (bom_line.product_id.default_code or "",
                                         bom_line.product_id.name),
                    'order_id': line.order_id.id})
            line.unlink()

    @api.multi
    def action_cancel(self):
        for record in self:
            if super(SaleOrder, record).action_cancel():
                record.write({'picking_pending': False})

    @api.multi
    def action_unlink_product_line(self):
        self.ensure_one()
        lines = self.order_line.filtered(
            lambda l: l.mrp_bom_id.id in self.mrp_bom_ids.ids)
        lines.unlink()

    # @api.depends('order_line', 'order_line.product_id',
    #              'order_line.mrp_bom_id')
    # def _compute_mrp_bom_lines(self):
    #     if self.order_line:
    #         self.mrp_bom_ids = self.order_line.mapped('mrp_bom_id')