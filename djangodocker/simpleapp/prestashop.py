# -*- coding: utf-8 -*-
import prestapyt
from . import models, mssql
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
import datetime
import logging
from . import controller

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
            return self._api.get('manufacturers', resource_id=manufacturer.ps_id)
        response = self._api.add('manufacturers', manufacturer.prestashop_object())
        manufacturer.ps_id = int(response['prestashop']['manufacturer']['id'])
        manufacturer.ps_name = manufacturer.icg_name
        manufacturer.updated = False
        manufacturer.save()
        return self._api.get('manufacturers', resource_id=manufacturer.ps_id)

    def get_or_create_product(self, product):
        if product.ps_id:
            return self._api.get('products', resource_id=product.ps_id)
        if not product.visible_web:
            return {}

        p_data = self._api.get('products', options={'schema': 'blank'})
        p_data['product']['id_manufacturer'] = product.manufacturer.ps_id
        p_data['product']['reference'] = product.icg_reference
        p_data['product']['price'] = 0
        p_data['product']['name']['language'] = self.update_language(
            p_data['product']['name']['language'], product.icg_name)
        p_data['product']['link_rewrite']['language'] = self.update_language(
            p_data['product']['link_rewrite']['language'], "link-rewrite")

        response = self._api.add('products', p_data)
        product.ps_id = int(response['prestashop']['product']['id'])
        product.updated = False
        product.save()

        #Create product options dj
        po_talla = self.get_or_create_product_options_django(product, 'talla')
        po_color = self.get_or_create_product_options_django(product, 'color')

        return self._api.get('products', resource_id=product.ps_id)

    def get_or_create_combination(self, comb):
        if comb.ps_id:
            return self._api.get('combinations', resource_id=comb.ps_id)
        response = self._api.add('combinations', comb.prestashop_object())
        comb.ps_id = int(response['prestashop']['combination']['id'])
        comb.updated = False
        comb.save()

        # Create product option values
        po_talla = self.get_or_create_product_options_django(comb.product_id, 'talla')
        po_color = self.get_or_create_product_options_django(comb.product_id, 'color')
        talla = self.get_or_create_product_option_value_django(po_talla, comb.icg_talla)
        color = self.get_or_create_product_option_value_django(po_color, comb.icg_color)

        return self._api.get('combinations', resource_id=comb.ps_id)

    def get_or_create_product_options_django(self, product, tipus):
        c = controller.ControllerICGProducts()
        ps_name = str(str(product.ps_id) + "_" + tipus)
        return c.get_create_or_update('ProductOption', {'ps_name' : ps_name, 'product_id': product}, {})

    def get_or_create_product_option_value_django(self, po, icg_name):
        c = controller.ControllerICGProducts()
        return c.get_create_or_update('ProductOptionValue', {'po_id' : po, 'icg_name': icg_name}, {})

    def get_or_create_product_options(self, po):
        if po.ps_id:
            return self._api.get('product_options', resource_id=po.ps_id)
        
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
        po.updated = False
        po.save()
        return self._api.get('product_options', resource_id=po.ps_id)

    def get_or_create_product_option_value(self, pov):
        #import pudb;pu.db
        if pov.ps_id:
            return self._api.get('product_option_values', resource_id=pov.ps_id)
 
        pov_data = self._api.get('product_option_values', options={'schema': 'blank'})
        pov_data['product_option_value']['id_attribute_group'] = pov.po_id.ps_id
        pov_data['product_option_value']['name']['language'] = self.update_language(
            pov_data['product_option_value']['name']['language'], pov.icg_name)

        response = self._api.add('product_option_values', pov_data)
        pov.ps_id = int(response['prestashop']['product_option_value']['id'])
        pov.save()
        return self._api.get('product_option_values', pov.ps_id)

    def get_or_create_specific_price(self, price):
        if price.ps_id:
            return self._api.get('specific_prices', resource_id=price.ps_id)

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
        return self._api.get('specific_prices', resource_id=price.ps_id)

    def update_manufacturer(self, man_dj, man_ps, updated):
        man_ps.update(man_dj.prestashop_object())
        man_ps['manufacturer']['id'] = man_dj.ps_id
        response = self._api.edit('manufacturers', man_ps)
        man_dj.ps_id = int(response['prestashop']['manufacturer']['id'])
        man_dj.ps_name = man_dj.icg_name
        man_dj.updated = False
        man_dj.save()

    def updated_product(self, prod_dj, prod_ps, updated):
        prod_ps.update(prod_dj.prestashop_object())
        prod_ps['product']['id'] = prod_dj.ps_id
        response = self._api.edit('products', prod_ps)
        prod_dj.ps_id = int(response['prestashop']['product']['id'])
        prod_dj.ps_name = prod_dj.icg_name
        prod_dj.updated = False
        prod_dj.save()

    def updated_combination(self, comb_dj, comb_ps, updated):
        if 'discontinued' in updated:
            return self._api.delete('combinations', resource_ids=comb_dj.ps_id)
        comb_ps.update(updated)
        response = self._api.edit('combinations', prod_ps)
        comb_dj.updated = False
        comb_dj.save()
        return response

    def carregaNous(self):
        ps_man = []
        updated_manufacturers = models.Manufacturer.objects.filter(updated = True)
        for man in updated_manufacturers:
            m = self.get_or_create_manufacturer(man)
            ps_man.append(m['manufacturer']['id'])
            updated = man.compare(m)
            if updated:
                self.update_manufacturer(man, m, updated)

        ps_prod = []
        updated_products = models.Product.objects.filter(updated = True)
        for prod in updated_products:
            p = self.get_or_create_product(prod)
            ps_prod.append(p['product']['id'])
            updated = prod.compare(p)
            if updated:
                self.updated_product(prod, p, updated)

        ps_po = []
        updated_product_options = models.ProductOption.objects.filter(updated = True)
        for po in updated_product_options:
            p = self.get_or_create_product_options(po)
            ps_po.append(p['product_option']['id'])

        ps_pov = []
        updated_product_options_values = models.ProductOptionValue.objects.filter(updated = True)
        for pov in updated_product_options_values:
            p = self.get_or_create_product_option_value(pov)
            ps_pov.append(p['product_option_value']['id'])

        ps_comb = []
        updated_comb = models.Combination.objects.filter(updated = True)
        for comb in updated_comb:
            c = self.get_or_create_combination(comb)
            ps_comb.append(c['combination']['id'])
            updated = comb.compare(c)
            if updated:
                #import pudb;pu.db
                self.updated_combination(comb, c, updated)
                #if deleted, ps_comb.remove


        return {'ps_man': ps_man, 'ps_prod': ps_prod, 'ps_po': ps_po,
            'ps_pov': ps_pov, 'ps_comb': ps_comb}

# vim: et ts=4 sw=4
