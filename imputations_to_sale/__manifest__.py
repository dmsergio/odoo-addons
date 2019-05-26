# -*- encoding: utf-8 -*-
{
    "name": "Imputations To Sales",
    "version": "10.0.0.0.3",
    "author": "Sergio Díaz",
    "category": "Human Resources",
    "website": "",
    "summary": "Impute employee costs to sale orders",
    "depends": [
        "product",
        "sale",
        "sales_team"
    ],
    "data": [
        'views/product_template_view.xml',
        'views/sale_order_line.xml',
        'views/impute_to_sale_wiz_view.xml',
        'views/impute_hours_wiz_view.xml',
        'views/res_partner_view.xml',
    ],
    "active": False,
    "installable": True,
}
