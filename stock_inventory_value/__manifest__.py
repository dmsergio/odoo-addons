# -*- encoding: utf-8 -*-
# Copyright 2019 Sergio Díaz  <sdimar@yahoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Stock Inventory Value',
    'version': '10.0.0.0.1',
    'depends': [
        'base',
        'stock'
    ],
    'author': 'sdimar@yahoo.com',
    'website': '',
    'category': 'Stock',
    'description': '''
    Addon that allow save a history of inventory value daily.
    ''',
    'data': [
        'data/cron.xml',
        # security
        'security/ir.model.access.csv',
        # views
        'views/stock_value.xml'],
    'installable': True,
    'auto_install': False,
}