# -*- encoding: utf-8 -*-
# Copyright 2019 Sergio Díaz  <sdimar@yahoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    parent_receivable_account_id =  fields.Many2one(
        comodel_name='account.account',
        string='Receivable Account',
        domain="[('internal_type','=','receivable'),('company_id','=',active_id)]",
        help='If set, a receivable account will be created for all partners with the "Customer" flag set.')

    parent_payable_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Payable Account',
        domain="[('internal_type','=','payable'),('company_id','=',active_id)]",
        help='If set, a payable account will be created for all partners with the "Supplier" flag set.')

    account_digits = fields.Integer(
        string='Number of digits',
        help='Indicates the number of digits to be used for automatically created receivable and payable partner '
             'accounts.')
