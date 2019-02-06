# -*- encoding: utf-8 -*-
# Copyright 2019 Sergio Díaz  <sdimar@yahoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Partner Auto Account',
    'version': '10.0.0.0.1',
    'depends': [
        'base',
        'account',
        # 'base_partner_sequence'
    ],
    'author': 'sdimar@yahoo.com',
    'website': '',
    'category': 'Account',
    'description': '''
    Create customer and supplier account with the partner sequence number.
    
    Based in nan_account_extension (NaN Projectes de Programari Lliure, S.L.)
    
    ''',
    'data': [
        'views/company_view.xml'],
    'installable': True,
    'auto_install': False,
}