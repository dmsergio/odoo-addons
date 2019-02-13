# -*- encoding: utf-8 -*-
# Copyright 2019 Sergio Díaz  <sdimar@yahoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def update_account(self, partner_id, account_type, force_checked=None):

        if account_type not in ('receivable', 'payable'):
            return

        company_id = self.env.user.company_id
        parent_account = getattr(company_id, 'parent_%s_account_id' % account_type )
        if not parent_account:
            return

        if account_type == 'receivable':
            checked = partner_id.customer
        else:
            checked = partner_id.supplier
        partner_account = getattr(partner_id, 'property_account_%s_id' % account_type )

        if not force_checked is None:
            checked = force_checked

        if partner_account:
            if checked:
                # If account already exists, just check if we need to update account name.
                if partner_account.name != partner_id.name:
                    # We will only update account name if no other partner is using the same account.
                    value = 'account.account,%d' % partner_account.id
                    ir_property_obj = self.env['ir.property']
                    partners = ir_property_obj.search([
                        ('res_id','!=',False),
                        ('value_reference','=',value)])
                    if len(partners) == 1:
                        partner_account.write({'name': partner_id.name})
                        return

            # If it's not possible to unlink the account we will rollback this change
            # so the property remains the same. Note that we cannot try to unlink first,
            # because in this case it would always fail because of the fact that it's set
            # as the account in the partner.
            self.env.cr.execute('SAVEPOINT remove_account')
            self.write({
                'property_account_%s_id' % account_type : False})
            try:
                # Unlink may raise an exception if the account is already set in another partner
                # or if it has account moves.
                if partner_account.name == partner_id.name:
                    partner_account.unlink()
                    # self.pool.get('account.account').unlink(cr, uid, [partner_account.id], context)
            except Exception:
                self.env.cr.execute('ROLLBACK TO SAVEPOINT remove_account')

            self.env.cr.execute('RELEASE SAVEPOINT remove_account')

        if not checked:
            return
        sequence_obj = self.env['ir.sequence']
        sequence_id = sequence_obj.search([('code','=','res.partner')])

        partner_ref = partner_id.ref or ''
        digits = company_id.account_digits or 0
        code = parent_account.code + '0'*(digits - len(parent_account.code + partner_ref)) + partner_ref

        account_obj = self.env['account.account']
        account_id = account_obj.search([('code','=',code)])
        if account_id:
            account_id = account_id[0]
        else:
            account_id = account_obj.create({
                'name': partner_id.name,
                'code': code,
                'parent_id': parent_account.id,
                'user_type_id': parent_account.user_type_id.id,
                'reconcile': True,
                'type': account_type})
        self.write({'property_account_%s' % account_type: account_id.id})

    @api.model
    def create(self, values):
        partner_id = super(ResPartner, self).create(values)
        self.update_account(partner_id, 'receivable')
        self.update_account(partner_id, 'payable')
        return partner_id

    @api.one
    def write(self, values):
        result = super(ResPartner, self).write(values)
        if 'customer' in values or 'name' in values:
            partner_id = self
            self.update_account(partner_id, 'receivable')
        if 'supplier' in values or 'name' in values:
            partner_id = self
            self.update_account(partner_id, 'payable')
        return result

    @api.one
    def unlink(self):
        partner_id = self
        self.update_account(partner_id, 'receivable', force_checked = False)
        self.update_account(partner_id, 'payable', force_checked = False)
        return super(ResPartner, self).unlink()
