# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    def _amount_all(self):
        self.update({
            "amount_tax": sum(self.order_line.mapped("price_tax")),
            "amount_untaxed": sum(self.order_line.mapped("price_subtotal")),
            "amount_total": sum(self.order_line.mapped("price_total"))})
