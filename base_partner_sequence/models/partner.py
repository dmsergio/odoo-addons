# -*- coding: utf-8 -*-
# © 2004-2009 Tiny SPRL (<http://tiny.be>).
# © 2013 initOS GmbH & Co. KG (<http://www.initos.com>).
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class ResPartner(models.Model):
    """Assigns 'ref' from a sequence on creation and copying"""

    _inherit = 'res.partner'

    @api.model
    def _needsRef(self, partner_id=None, values=None):
        """
        Checks whether a sequence value should be assigned to a partner's 'ref'

        :param partner_id: res.partner object
        :param values: known field values of the partner object
        :return: true if a sequence value should be assigned to the partner's 'ref'
        """
        if not values and not partner_id:
            raise Exception('Either field values or an id must be provided.')
        if values is None:
            values = {}
        _values = values.copy()
        # only assign a 'ref' to commercial partners
        if partner_id:
            _values.setdefault('is_company',  partner_id.is_company)
            _values.setdefault('parent_id', partner_id.parent_id.id)
        return _values.get('is_company') or not _values.get('parent_id')

    @api.model
    def _commercial_fields(self):
        """
        Make the partner reference a field that is propagated
        to the partner's contacts
        """
        return super(ResPartner, self)._commercial_fields() + ['ref']

    @api.model
    def _get_next_ref(self):
        return self.env['ir.sequence'].next_by_code('res.partner')

    @api.model
    def create(self, values):
        if not values.get('ref') and self._needsRef(values=values):
            values['ref'] = self._get_next_ref()
        return super(ResPartner, self).create(values)

    @api.multi
    def write(self, values):
        for partner_id in self:
            ref = values.get('ref') if 'ref' in values else partner_id.ref
            if not ref and self._needsRef(partner_id, values):
                values['ref'] = self._get_next_ref()
            super(ResPartner, partner_id).write(values)
        return True

    @api.multi
    def copy(self, values=None):
        _values = values or {}
        if self._needsRef(self):
            _values['ref'] = self._get_next_ref()
        return super(ResPartner, self).copy(_values)
