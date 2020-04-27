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

    def update_language(self, language, name):
        if isinstance(language, list):
            for lang in language:
                lang['value'] = name
        else:
            language['value'] = name
        return language

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

    def get_or_create_product_option_value(self, pov):
        if pov.ps_id:
            self._api.get('product_option_values', resource_id=pov.ps_id)
            return pov
 
        pov_data = self._api.get('product_option_values', options={'schema': 'blank'})
        pov_data['product_option_value']['id_attribute_group'] = pov.po_id.ps_id
        pov_data['product_option_value']['name']['language'] = self.update_language(
            pov_data['product_option_value']['name']['language'], pov.icg_name)

        response = self._api.add('product_option_values', pov_data)
        pov.ps_id = int(response['prestashop']['product_option_value']['id'])
        pov.save()
        return pov

    def get_or_create_specific_price(self, price):
        if price.ps_id:
            self._api.get('specific_prices', resource_id=price.ps_id)
            return price

        price_data = self._api.get('specific_prices', options={'schema': 'blank'})
        price_data['specific_price']['id_product'] = price.combination_id.product_id.ps_id
        price_data['specific_price']['id_product_attribute'] = price.combination_id.ps_id
        price_data['specific_price']['id_shop'] = 0
        price_data['specific_price']['id_cart'] = 0
        price_data['specific_price']['id_currency'] = 0
        price_data['specific_price']['id_country'] = 0
        price_data['specific_price']['id_group'] = 0
        price_data['specific_price']['id_customer'] = 0
        price_data['specific_price']['price'] = 0
        price_data['specific_price']['reduction_tax'] = 0
        price_data['specific_price']['from'] = '0000-00-00 00:00:00'
        price_data['specific_price']['to'] = '0000-00-00 00:00:00'
        price_data['specific_price']['reduction'] = price.dto_percent / 100;
        price_data['specific_price']['reduction_type'] = 'percentage';
        price_data['specific_price']['from_quantity'] = 1;

        response = self._api.add('specific_prices', price_data)
        price.ps_id = int(response['prestashop']['specific_price']['id'])
        price.updated = False
        price.save()
        return price

