# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OrderList:
    my_list = []

class account_move_line(models.Model):
    _inherit = 'account.move.line'

    remaining_amount = fields.Float(
        "Saldo pendiente",
        compute="_get_balance")

    @api.multi
    @api.depends('balance')
    def _get_balance(self):
        move_line_ids = OrderList.my_list
        sorted(move_line_ids, key=lambda x: 'x.date, x.move_id.name, x.id')
        amount = 0.0
        for line in move_line_ids:
            amount = amount + line.balance
            line.remaining_amount = amount
        return True

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """
        Override default search function so that if it's being called from the
        statement of accounts tree view, the given order is ignored and a
        special one is used so it ensures consistency between balance field
        value and account.move.line order.
        """
        context = self._context or {}
        move_ids = super(account_move_line, self).search(
            args, offset, limit, order, count)
        OrderList.my_list = move_ids
        return super(account_move_line, self).search(
                 args, offset, limit, order, count)
    #     if context.get('statement_of_accounts'):
    #         if move_ids:
    #             if isinstance(move_ids, (long, int)):
    #                 move_ids = [move_ids]
    #             # If it's a statement_of_accounts, ignore order given
    #             move_ids = ','.join([str(int(x)) for x in move_ids])
    #             # This sorting criteria must be the one used by the 'balance'
    #             # functional field above, so remember to modify that if you want
    #             # to change the order.
    #             self.env.cr.execute("""
    #                 SELECT aml.id
    #                 FROM account_move_line aml, account_move am
    #                 WHERE aml.move_id = am.id AND am.name != '/'
    #                     AND aml.id IN (%s)
    #                 ORDER BY
    #                     LPAD(EXTRACT(EPOCH FROM aml.date)::VARCHAR, 15, '0') ||
    #                         LPAD(am.name,15,'0') ||
    #                         LPAD(aml.id::VARCHAR,15,'0')""" % move_ids)
    #             result = self.env.cr.fetchall()
    #             ids = [x[0] for x in result]
    #             args.append((('id', 'in', ids)))
    #     return super(account_move_line, self).search(
    #         args, offset, limit, order, count)
