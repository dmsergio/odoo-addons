# -*- coding: utf-8 -*-
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


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
