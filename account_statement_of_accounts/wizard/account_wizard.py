# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime


class accountStatementAccountsWizard(models.TransientModel):
    _name = 'account.statement.accounts.wizard'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self._get_default_company())

    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Acount',
        required=True)

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner')

    date_ini = fields.Date(
        string='Date Start',
        required=True,
        default=fields.Date.from_string("{}-01-01".format(
            datetime.today().year)))

    date_end = fields.Date(
        string='Date End',
        required=True,
        default=fields.Date.to_string(datetime.today()))

    @api.depends('company_id')
    def _get_default_company(self):
        return self.env.user.company_id.id

    @api.multi
    def action_open(self):
        """
        this function shows all the movements of an account in a given time
        :return: list view
        """
        name = self.partner_id and self.partner_id.name or self.account_id.name
        title = '%s : %s' % (self.account_id.code, name)
        if len(name) > 10:
            title += '...'

        if self.date_ini > self.date_end:
            tmp_date = self.date_ini
            self.date_ini = self.date_end
            self.date_end = tmp_date

        self.date_ini += ' 00:00:00'
        self.date_end += ' 23:59:59'

        domain = [
            ('account_id', '=', self.account_id.id),
            ('date', '>=', self.date_ini),
            ('date', '<=', self.date_end)]

        view_id = self.env.ref('account_statement_of_accounts.'
                               'account_move_line_statement_of_accounts_view')
        ctx = self.env.context.copy()
        ctx['active_ids'] = self.ids
        ctx['statement_of_accounts'] = True
        ctx['view_mode'] = True
        ctx['date_ini'] = self.date_ini
        ctx['date_end'] = self.date_end

        if self.partner_id:
            domain += [('partner_id', '=', self.partner_id.id)]
            ctx['partner_id'] = self.partner_id.id
        return {
            'view_type': 'form',
            'view_mode': 'tree, form',
            'views': [(view_id.id, 'tree'), (False, 'form')],
            'context': ctx,
            'domain': domain,
            'limit': 500,
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'name': title}

    def onchange_method(self, partner_id):
        """
        Search if the account is paid or copper on the customer / supplier tab
        :return: value
        """
        value = {}
        if partner_id:
            obj_partner = self.env['res.partner']
            partner = obj_partner.browse(partner_id)
            if partner.customer:
                value['account_id'] = \
                    (partner.property_account_receivable_id.name and
                     partner.property_account_receivable_id.id) or 0
            elif partner.supplier:
                value['account_id'] = \
                    (partner.property_account_payable_id.name and
                     partner.property_account_payable_id.id) or 0
            else:
                value['account_id'] = \
                    (partner.property_account_receivable_id.name and
                     partner.property_account_receivable_id.id) or 0
        else:
            value['account_id'] = 0
        return {'value': value}
