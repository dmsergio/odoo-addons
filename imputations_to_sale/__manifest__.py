# -*- encoding: utf-8 -*-
{
    "name": "Imputations To Sales",
    "version": "10.0.0.0.5",
    "author": "Sergio Díaz & Jesús Ndong",
    "category": "Human Resources",
    "website": "",
    "summary": "Impute employee costs to sale orders",
    "depends": [
        "product",
        "l10n_es",
        "sale",
        "sale_margin",
        "sales_team",
        "mejisa"
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/manual_product_template.xml',
        'data/mejisa_product_pricelist_data.xml',
        'views/account_invoice.xml',
        'views/product_template_view.xml',
        'views/sale_order_line.xml',
        'views/impute_hours_wiz_view.xml',
        'views/impute_material_to_sale.xml',
        'views/res_partner_view.xml',
        'views/mejisa_product_pricelist.xml',
    ],
    "active": False,
    "installable": True,
}
