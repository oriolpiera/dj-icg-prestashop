# -*- coding: utf-8 -*-
import prestapyt
from . import models, mssql
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
import datetime
import logging

class ControllerPrestashop(object):
    def __init__(self, url_base=''):
        self._url_base = url_base
        self.logger = logging.getLogger(__name__)
        self._api =  prestapyt.PrestaShopWebServiceDict(
            'http://prestashop/api', 'GENERATE_COMPLEX_KEY_LIKE_THIS!!', debug=True, verbose=True)

    def get_or_create_manufacturer(self, manufacturer):
        if manufacturer.ps_id:
            self._api.get('manufacturers', resource_id=manufacturer.ps_id)
            return manufacturer
        response = self._api.add('manufacturers', manufacturer.prestashop_object())
        manufacturer.ps_id = int(response['prestashop']['manufacturer']['id'])
        manufacturer.updated = False
        manufacturer.save()
        return manufacturer

    def get_or_create_product(self, product):
        if product.ps_id:
            self._api.get('products', resource_id=product.ps_id)
            return product
        response = self._api.add('products', product.prestashop_object())
        product.ps_id = int(response['prestashop']['product']['id'])
        product.updated = False
        product.save()
        return product

    def get_or_create_combination(self, comb):
        if comb.ps_id:
            self._api.get('combinations', resource_id=comb.ps_id)
            return comb
        response = self._api.add('combinations', comb.prestashop_object())
        comb.ps_id = int(response['prestashop']['combination']['id'])
        comb.updated = False
        comb.save()
        return comb

    def update_language(self, language, name):
        if isinstance(language, list):
            for lang in language:
                lang['value'] = name
        else:
            language['value'] = name
        return language

    def get_or_create_product_options(self, po):
        if po.ps_id:
            self._api.get('product_options', resource_id=po.ps_id)
            return po
        
        po.ps_name = str(po.product_id.ps_id) + "_" + po.ps_icg_type
        po.ps_public_name = str(po.product_id.ps_id) + "_" + po.ps_icg_type

        po_data = self._api.get('product_options', options={'schema': 'blank'})
        po_data['product_option']['group_type'] = 'select'
        po_data['product_option']['name']['language'] = self.update_language(
            po_data['product_option']['name']['language'], po.ps_name)
        po_data['product_option']['public_name']['language'] = self.update_language(
            po_data['product_option']['public_name']['language'], po.ps_public_name)

        response = self._api.add('product_options', po_data)
        po.ps_id = int(response['prestashop']['product_option']['id'])
        po.save()
        return po

    def get_or_create_price(self, price):
        if price.combination_id.ps_id:
            self._api.get('combinations', resource_id=comb.ps_id)
            return comb
        response = self._api.add('combinations', price.combproduct.prestashop_object())
        comb.ps_id = int(response['prestashop']['combination']['id'])
        comb.updated = False
        comb.save()
        return comb

