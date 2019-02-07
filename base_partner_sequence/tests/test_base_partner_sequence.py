# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV (<http://acsone.eu>).
# © 2019 Sergio Díaz (<sdimar@yahoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestBasePartnerSequence(TransactionCase):

    def test_ref_sequence_on_partner(self):
        res_partner = self.env['res.partner']
        partner_id = res_partner.create({
            'name': "test1",
            'email': "test@test.com"})
        self.assertTrue(partner_id.ref, "A partner has always a ref.")

        # copy = partner_id.copy()
        # self.assertTrue(copy.ref, "A partner with ref created by copy "
        #                 "has a ref by default.")
