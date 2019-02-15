# -*- coding: utf-8 -*-
{
    "name": "Statment of Accounts",
    "version": "10.0.0.0.1",
    "author": "Jesus Pablo Ndong Nguema",
    "category": "Accounting",
    "website": "http://www.nan-tic.com",
    "description": """\
        This module adds a new menu entry to show statements of accounts.

        Unreconciled account move lines are shown in red and partially
         reconcilled ones are shown in blue.
        """,
    "contributors": [
        'Jesus Pablo Ndong',
        'sdimar@yahoo.es'],
    "depends": [
        'account',
        ],
    "data": [
        'views/account_view.xml',
        'wizard/account_wizard.xml',
    ],
    'application': True,
}
