# -*- encoding: utf-8 -*-
# Copyright 2019 Sergio Díaz  <sdimar@yahoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def default_get(self, fields):
        res = super(ProductTemplate, self).default_get(fields)
        if 'search_default_filter_to_purchase' in self._context:
            res = self.get_default_fields(res)
            res = self.get_default_fields_purchase(res)
        elif 'search_default_filter_to_sell' in self._context or 'search_default_consumable' in self._context:
            res = self.get_default_fields(res)
            res = self.get_default_fields_sale(res)
        return res

    def get_default_fields(self, field_values):
        """
        Function to prepare the default fields to return in the product.template view
        :param fields: dict
        :return: dict
        """
        # objects needed
        account_obj = self.env['account.account']
        # records
        account_income_id = account_obj.search([
            ('code', '=', '70000000')])
        account_expense_id = account_obj.search([
            ('code', '=', '60000000')])
        account_creditor_id = account_obj.search([
            ('code', '=', '60700000')])
        field_values.update({
            'list_price': 0.0,
            'property_account_income_id': account_income_id.id or False,
            'property_account_expense_id': account_expense_id.id or False,
            'property_account_creditor_price_difference': account_creditor_id.id or False})
        return field_values

    def get_default_fields_purchase(self, field_values):
        """
        Function to prepare the default fields to return in the product.template view
        :param fields: dict
        :return: dict
        """
        # objects needed
        product_uom_obj = self.env['product.uom']
        product_category_obj = self.env['product.category']
        # records
        product_uom_id = product_uom_obj.search([('name', '=', 'mm')])
        product_category_id = product_category_obj.search([('name', '=', 'MATERIAS PRIMAS')])
        field_values.update({
            'type': 'product',
            'uom_id': product_uom_id.id or False,
            'uom_po_id': product_uom_id.id or False,
            'categ_id': product_category_id.id or False,
            'tracking': 'lot'})
        return field_values

    def get_default_fields_sale(self, field_values):
        """
        Function to prepare the default fields to return in the product.template view
        :param fields: dict
        :return: dict
        """
        # objects needed
        product_category_obj = self.env['product.category']
        # records
        product_category_parent_id = product_category_obj.search([
            ('name', '=', 'PRODUCTO ACABADO')])
        product_category_id = product_category_obj.search([
            ('name', '=', 'MECANIZADO'),
            ('parent_id', '=', product_category_parent_id.id)])
        field_values.update({
            'categ_id': product_category_id.id or False,
            'route_ids': [(6, 0, [1])]})
        return field_values