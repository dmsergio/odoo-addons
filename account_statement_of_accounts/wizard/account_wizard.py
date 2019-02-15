# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date, datetime
import psycopg2

class account_move_line(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def search(self, args, offset=0, limit=None, order=None):
        """
        Override default search function so that if it's being called from the statement of accounts
        tree view, the given order is ignored and a special one is used so it ensures consistency
        between balance field value and account.move.line order.
        """
        context = self._context or {}
        move_ids = super(account_move_line, self).search(args, offset, limit, order)
        if context.get('statement_of_accounts'):
            if move_ids:
                if isinstance(move_ids, (long, int)):
                    move_ids = [move_ids]
                # If it's a statement_of_accounts, ignore order given
                move_ids = ','.join([str(int(x)) for x in move_ids])
                # This sorting criteria must be the one used by the 'balance' functional field above,
                # so remember to modify that if you want to change the order.
                self.env.cr.execute("""
                    SELECT aml.id
                    FROM account_move_line aml, account_move am
                    WHERE aml.move_id = am.id AND am.name != '/'
                        AND aml.id IN (%s)
                    ORDER BY 
                        LPAD(EXTRACT(EPOCH FROM aml.date)::VARCHAR, 15, '0') || 
                            LPAD(am.name,15,'0') || 
                            LPAD(aml.id::VARCHAR,15,'0')""" % move_ids)
                result = self.env.cr.fetchall()
                ids = [x[0] for x in result]
                args.append((('id', 'in', ids)))
        return super(account_move_line, self).search(args, offset, limit, order)


class accountStatementAccountsWizard(models.TransientModel):
    _name = 'account.statement.accounts.wizard'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company', required=True,
        default=lambda self: self._get_default_company())

    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Acount', required=True)

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner')

    date_ini = fields.Date(
        string='Date Start', required=True)

    date_end = fields.Date(
        string='Date End', required=True,
        default=fields.Date.to_string(datetime.today()))

    @api.depends('company_id')
    def _get_default_company(self):
        user_obj = self.env['res.users']
        user_id = self._context['uid']
        user = user_obj.browse(user_id)
        return user.company_id.id

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

        view_id = self.env.ref('account_statement_of_accounts.account_move_line_statement_of_accounts_view')
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
                    (partner.property_account_receivable_id.name and partner.property_account_receivable_id.id) or 0
            elif partner.supplier:
                value['account_id'] = \
                    (partner.property_account_payable_id.name and partner.property_account_payable_id.id) or 0
            else:
                value['account_id'] = \
                    (partner.property_account_receivable_id.name and partner.property_account_receivable_id.id) or 0
        else:
            value['account_id'] = 0
        return {'value': value}





