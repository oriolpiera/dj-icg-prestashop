# -*- coding: utf-8 -*-
import prestapyt
from . import models, mssql
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
import datetime
import logging
from . import controller, constants, mytools

class ControllerPrestashop(object):
    def __init__(self):
        self.logger = logging.getLogger("django")
        self._api =  prestapyt.PrestaShopWebServiceDict(
            constants.PS_URL, constants.PS_KEY, debug=True, verbose=True)

    def escapeSpecialChars(self, name):
        return name.replace("{","").replace("}","").replace("'","")

    def update_language(self, language, name):
        if isinstance(language, list):
            for lang in language:
                lang['value'] = name
        else:
            language['value'] = name
        return language


    def tryToUpdateProduct_fromPS(self, product):
        if product.icg_reference:
            response = self._api.get('products', None,
                {'filter[reference]': product.icg_reference, 'limit': '1'})
            if response['products']:
                #Product exist
                product.ps_id = int(response['products']['product']['attrs']['id'])
                product.save()
                return True

    def tryToUpdateProductOption_fromPS(self, po):
        if po.ps_name:
            response = self._api.get('product_options', None,
                {'filter[reference]': product.icg_reference, 'limit': '1'})
            if response['products']:
                #Product exist
                product.ps_id = int(response['products']['product']['attrs']['id'])
                product.save()
                return True

    def tryToUpdateSpecificPrice_fromPS(self, sp):
        if sp.ps_id:
            response = self._api.get('specific_prices', sp.ps_id)
            if response['specific_prices']:
                #Discount exist
                sp.ps_combination_id = int(response['specific_prices']['specific_price']['id_product_attribute'])
                sp.ps_reduction = float(response['specific_prices']['specific_price']['reduction'])
                sp.save()
                return True

    def get_or_create_category(self, category):
        if category.ps_id:
            try:
                response = self._api.get('categories', resource_id=category.ps_id)
            except prestapyt.prestapyt.PrestaShopWebServiceError:
                #No exist in PS anymore. Recreate
                category.ps_id = 0
                category.save()
                return self.get_or_create_category(category)
        else:
            p_data = self._api.get('categories', options={'schema': 'blank'})
            p_data['category']['name'] = mytools.update_ps_dict(
                p_data['category']['name'], category, 'ps_name')
            p_date['category']['link_rewrite'] = mytools.update_ps_dict(
                p_data['category']['link_rewrite'], category, 'ps_link_rewrite')
            p_date['category']['description'] = mytools.update_ps_dict(
                p_data['category']['description'], category, 'ps_description')
            p_date['category']['meta_title'] = mytools.update_ps_dict(
                p_data['category']['meta_title'], category, 'ps_meta_title')
            p_date['category']['meta_description'] = mytools.update_ps_dict(
                p_data['category']['meta_description'], category, 'ps_meta_description')
            p_date['category']['meta_keywords'] = mytools.update_ps_dict(
                p_data['category']['meta_keywords'], category, 'ps_meta_keywords')
            p_data['category']['active'] = 1 if category.ps_active else 0
            response = self._api.add('categories', p_data)
            category.ps_id = int(response['prestashop']['category']['id'])
            category.ps_name = category.ps_name
            self.logger.info("Category created: %s", str(category.ps_name))
        response = self._api.get('categories', resource_id=category.ps_id)
        category.updated = False
        category.save()
        return response

    def get_or_create_manufacturer(self, manufacturer):
        if manufacturer.ps_id:
            try:
                response = self._api.get('manufacturers', resource_id=manufacturer.ps_id)
            except prestapyt.prestapyt.PrestaShopWebServiceError:
                #No exist in PS anymore. Recreate
                manufacturer.ps_id = 0
                manufacturer.save()
                return self.get_or_create_manufacturer(manufacturer)

            updated, new_man_ps = manufacturer.compare(response)
            if updated:
                new_man_ps['manufacturer'].pop('link_rewrite', None)
                response = self._api.edit('manufacturers', new_man_ps)
                self.logger.info("Manufacturer modificat: %s", str(new_man_ps))
        else:
            if manufacturer.ps_name:
                response = self._api.get('manufacturers', None,
                    {'filter[name]': manufacturer.ps_name, 'limit': '1'})
                if response['manufacturers']:
                    #Product exist
                    manufacturer.ps_id = int(response['manufacturers']['manufacturer']['attrs']['id'])
                    manufacturer.save()
                    return self.get_or_create_manufacturer(manufacturer)
            p_data = self._api.get('manufacturers', options={'schema': 'blank'})
            p_data['manufacturer']['name'] = manufacturer.icg_name
            response = self._api.add('manufacturers', p_data)
            manufacturer.ps_id = int(response['prestashop']['manufacturer']['id'])
            manufacturer.ps_name = manufacturer.icg_name
            self.logger.info("Manufacturer creat: %s", str(manufacturer.icg_name))
        response = self._api.get('manufacturers', resource_id=manufacturer.ps_id)
        manufacturer.updated = False
        manufacturer.save()
        return response

    def get_or_create_product(self, product):
        if product.ps_id:
            try:
                response = self._api.get('products', resource_id=product.ps_id)
            except prestapyt.prestapyt.PrestaShopWebServiceError:
                #No exist in PS anymore. Recreate
                product.ps_id = 0
                product.save()
                return self.get_or_create_product(product)

            updated, new_prod_ps = product.compare(response)

            if not product.visible_web:
                new_prod_ps['product'].pop('manufacturer_name', None)
                new_prod_ps['product'].pop('quantity', None)
                new_prod_ps['product'].pop('position_in_category', None)
                new_prod_ps['product']['active'] = 0
                new_prod_ps['product']['id_category_default'] = constants.NO_VISIBLE_CATEGORY
                response = self._api.edit('products', new_prod_ps)
                self.logger.info("Producte modificat: %s", str(new_prod_ps))
                response = self._api.get('products', resource_id=product.ps_id)
            if updated:
                if not product.visible_web:
                    new_prod_ps['product']['active'] = 0
                    new_prod_ps['product']['id_category_default'] = constants.NO_VISIBLE_CATEGORY
                else:
                    new_prod_ps['product']['active'] = 1
                    new_prod_ps['product']['available_for_order'] = 1
                    try:
                        if isinstance(response['product']['associations']['categories']['category'], list):
                            new_prod_ps['product']['id_category_default'] = response['product']['associations']['categories']['category'][0]['id']
                        else:
                            new_prod_ps['product']['id_category_default'] = response['product']['associations']['categories']['category']['id']
                    except KeyError as e:
                        pass

                new_prod_ps['product'].pop('manufacturer_name', None)
                new_prod_ps['product'].pop('quantity', None)
                new_prod_ps['product'].pop('position_in_category', None)
                response = self._api.edit('products', new_prod_ps)
                self.logger.info("Producte modificat: %s", str(new_prod_ps))
                response = self._api.get('products', resource_id=product.ps_id)
        elif not product.visible_web:
            response = {}
        else:
            if product.icg_reference:
                response = self._api.get('products', None,
                    {'filter[reference]': product.icg_reference, 'limit': '1'})
                if response['products']:
                    #Product exist
                    product.ps_id = int(response['products']['product']['attrs']['id'])
                    product.save()
                    return self.get_or_create_product(product)
            p_data = self._api.get('products', options={'schema': 'blank'})
            if product.manufacturer:
                p_data['product']['id_manufacturer'] = product.manufacturer.ps_id
            else:
                p_data['product']['id_manufacturer'] = 0
            p_data['product']['reference'] = product.icg_reference
            p_data['product']['price'] = 0

            p_data['product']['position_in_category'] = 0
            if not product.iva:
                product.updateIVA()
            id_tax = constants.TAX_ID.get(product.iva)
            p_data['product']['id_tax_rules_group'] = id_tax
            p_data['product']['minimal_quantity'] = 1
            p_data['product']['state'] = 1
            #TODO: revisar active
            p_data['product']['active'] = 0
            p_data['product']['id_shop_default'] = 1
            p_data['product']['available_for_order'] = 1
            p_data['product']['show_price'] = 1
            p_data['product']['name']['language'] = self.update_language(
                p_data['product']['name']['language'], product.icg_name)
            p_data['product']['link_rewrite']['language'] = self.update_language(
                p_data['product']['link_rewrite']['language'], "link-rewrite")

            #Add Categories
            if product.ps_category_default:
                def_cat = self.get_or_create_category(product.ps_category_default)
                p_data['product']['id_category_default'] = def_cat['category']['id']
            else:
                p_data['product']['id_category_default'] = constants.ICG_CATEGORY
            cat_list = []
            for cat in product.ps_category_list.all():
                cat_list.append({'id': cat.ps_id})
            if len(cat_list) == 1:
                p_data['product']['associations']['categories'] = {'attrs': 
                    {'nodeType': 'category', 'api': 'categories'},'category': cat_list[0]}
            elif len(cat_list) > 1:
                p_data['product']['associations']['categories'] = {'attrs':
                    {'nodeType': 'category', 'api': 'categories'}, 'category': cat_list}
            elif len(cat_list) == 0:
                p_data['product']['associations']['categories'] = {'attrs': 
                    {'nodeType': 'category', 'api': 'categories'},'category': 251}

            response = self._api.add('products', p_data)
            product.ps_id = int(response['prestashop']['product']['id'])
            product.save()

            #Create product options dj
            po_talla = self.get_or_create_product_options_django(product, 'talla')
            po_color = self.get_or_create_product_options_django(product, 'color')
            response = self._api.get('products', resource_id=product.ps_id)

        product.updated = False
        product.save()
        return response

    def get_or_create_combination(self, comb, price=0):
        response = None
        if comb.ps_id:
            try:
                response = self._api.get('combinations', resource_id=comb.ps_id)
            except prestapyt.prestapyt.PrestaShopWebServiceError as e:
                #No exist in PS anymore. Recreate
                if comb.discontinued:
                    comb.ps_id = 0
                    comb.updated = False
                    comb.save()
                    return response
                comb.ps_id = 0
                comb.save()
                return self.get_or_create_combination(comb)
            updated, new_comb_ps = comb.compare(response)
            if price and (price != response['combination']['price']):
                new_comb_ps['combination']['price'] = price
                updated = True
            if updated:
                if 'discontinued' in new_comb_ps:
                    response = self._api.delete('combinations', resource_ids=comb.ps_id)
                    comb.ps_id = 0
                    self.logger.info("Combinacio eliminada: %s", str(comb))
                    comb.updated = False
                    comb.save()
                    return response
                else:
                    new_comb_ps['combination']['id'] = str(comb.ps_id)
                    #response = self._api.edit('combinations', comb.ps_id, new_comb_ps)
                    response_edit = self._api.edit('combinations', new_comb_ps)
                    self.logger.info("Combinacio modificada: %s", str(new_comb_ps))
        #We need to create combinations even when the product is not visible web
        elif comb.discontinued or comb.product_id.ps_id == 0:
        #elif comb.discontinued:
            comb.updated = False
            comb.save()
            return response
        else:
            # Create product option values
            po_talla = self.get_or_create_product_options_django(comb.product_id, 'talla')
            po_talla_ps = self.get_or_create_product_options(po_talla)
            po_color = self.get_or_create_product_options_django(comb.product_id, 'color')
            po_color_ps = self.get_or_create_product_options(po_color)
            talla = self.get_or_create_product_option_value_django(po_talla, comb.icg_talla)
            ps_talla = self.get_or_create_product_option_value(talla)
            color = self.get_or_create_product_option_value_django(po_color, comb.icg_color)
            ps_color = self.get_or_create_product_option_value(color)

            #Really combination not exist?
            comb_exist = self.combination_exist(comb.product_id.ps_id, ps_talla['product_option_value']['id'], ps_color['product_option_value']['id'])
            if comb_exist:
                comb.ps_id = int(comb_exist)
                comb.save()
                return self.get_or_create_combination(comb)

            p_data = self._api.get('combinations', options={'schema': 'blank'})
            p_data['combination']['id_product'] = comb.product_id.ps_id
            if comb.ean13 and comb.ean13 != ' ':
                p_data['combination']['ean13'] = comb.ean13
            p_data['combination']['price'] = price
            p_data['combination']['minimal_quantity'] = comb.minimal_quantity
            p_data['combination']['associations']['product_option_values']['product_option_value'] = []
            p_data['combination']['associations']['product_option_values']['product_option_value'].append({'id': ps_talla['product_option_value']['id']})
            p_data['combination']['associations']['product_option_values']['product_option_value'].append({'id': ps_color['product_option_value']['id']})
            response_add = self._api.add('combinations', p_data)
            comb.ps_id = int(response_add['prestashop']['combination']['id'])

        comb.updated = False
        comb.save()
        if not response:
            response = self._api.get('combinations', resource_id=comb.ps_id)

        return response

    def combination_exist(self, product_id, talla, color):
        response = self._api.get('combinations', None,
                    {'filter[id_product]': product_id})
        #self.logger.info("Estem a combination_exist")
        #self.logger.info(response)
        #self.logger.info(response['combinations'])
        if response['combinations'] and isinstance(response['combinations']['combination'], list):
            for comb in response['combinations']['combination']:
                combination = self._api.get('combinations', resource_id=comb['attrs']['id'])
                if isinstance(combination['combination']['associations']['product_option_values']['product_option_value'], list):
                    if ({'id': str(talla)} in
                        combination['combination']['associations']['product_option_values']['product_option_value']) and ({'id': str(color)} in 
                        combination['combination']['associations']['product_option_values']['product_option_value']):
                        return comb['attrs']['id']
        return False

    def get_or_create_price(self, price):
        c = self.get_or_create_combination(price.combination_id, price.pvp_siva)
        if c:
            price.ps_id = int(c['combination']['id'])
        price.updated = False
        price.save()
        return c

    def get_or_create_product_options_django(self, product, tipus):
        c = controller.ControllerICGProducts()
        ps_name = str(str(product.ps_id) + "_" + tipus)
        return c.get_create_or_update('ProductOption', {'ps_name' : ps_name},
                {'product_id': product, 'ps_icg_type': tipus})

    def get_or_create_product_option_value_django(self, po, icg_name):
        c = controller.ControllerICGProducts()
        return c.get_create_or_update('ProductOptionValue', {'po_id' : po, 'icg_name': icg_name}, {})

    def get_or_create_product_options(self, po):
        if po.ps_id:
            try:
                response = self._api.get('product_options', resource_id=po.ps_id)
            except prestapyt.prestapyt.PrestaShopWebServiceError:
                #No exist in PS anymore. Recreate
                po.ps_id = 0
                po.save()
                return self.get_or_create_product_options(po)
        #elif not po.product_id.visible_web:
        #    po.updated = False
        #    po.save()
        #    return False
        else:
            ps_name = str(po.product_id.ps_id) + "_" + po.ps_icg_type
            response = self._api.get('product_options', None,
                {'filter[name]': ps_name, 'limit': '1'})
            if response['product_options']:
                #Product options really exist
                po.ps_id = int(response['product_options']['product_option']['attrs']['id'])
                po.save()
                return self.get_or_create_product_options(po)

            po.ps_name = ps_name
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
        if pov.ps_id:
            try:
                response = self._api.get('product_option_values', resource_id=pov.ps_id)
            except prestapyt.prestapyt.PrestaShopWebServiceError:
                #No exist in PS anymore. Recreate
                pov.ps_id = 0
                pov.save()
                return self.get_or_create_product_option_value(pov)
        else:
            response = self._api.get('product_option_values', None,
                {'filter[id_attribute_group]': pov.po_id.ps_id})

            if response['product_option_values']:
                data = response['product_option_values']['product_option_value']
                if not isinstance(data, list):
                    data = [data]

                for p in data:
                    pov_ps_id = int(p['attrs']['id'])
                    pov_data = self._api.get('product_option_values', pov_ps_id)
                    temp_name = mytools.get_ps_language(
                        pov_data['product_option_value']['name']['language'])
                    if temp_name == pov.ps_name:
                        pov.ps_id = int(pov_data['product_option_value']['id'])
                        pov.save()
                        return self.get_or_create_product_option_value(pov)

            #Ok, let's create it
            pov_data = self._api.get('product_option_values', options={'schema': 'blank'})
            pov_data['product_option_value']['id_attribute_group'] = pov.po_id.ps_id
            pov_data['product_option_value']['name']['language'] = self.update_language(
                pov_data['product_option_value']['name']['language'], pov.ps_name)

            response = self._api.add('product_option_values', pov_data)
            pov.ps_id = int(response['prestashop']['product_option_value']['id'])

        pov.updated = False
        pov.save()
        return self._api.get('product_option_values', pov.ps_id)

    def get_or_create_specific_price(self, price):
        response = None
        if price.ps_id:
            try:
                response = self._api.get('specific_prices', resource_id=price.ps_id)
            except prestapyt.prestapyt.PrestaShopWebServiceError as e:
                #No exist in PS anymore. Recreate
                #if price.dto_percent == 0:
                #    raise prestapyt.prestapyt.PrestaShopWebServiceError(e)
                price.ps_id = 0
                price.save()
                return self.get_or_create_specific_price(price)

            updated, new_price_ps = price.comparePS(response)
            if updated:
                if float(new_price_ps['specific_price']['reduction']) == 0:
                    response = self._api.delete('specific_prices', resource_ids=price.ps_id)
                    price.ps_id = 0
                    self.logger.info("Descompte eliminat: %s", str(price))
                else:
                    new_price_ps['specific_price']['id'] = str(price.ps_id)
                    response_edit = self._api.edit('specific_prices', new_price_ps)
                    self.logger.info("Descompte modificat: %s", str(new_price_ps))
        elif not price.product_id:
            price.updated = False
            price.save()
            return False
        elif not price.product_id.ps_id:
            price.updated = False
            price.save()
            return False
        elif not price.dto_percent:
            price.updated = False
            price.save()
            return False
        else:
            if price.product_id.ps_id:
                response = self._api.get('specific_prices', None,
                    {'filter[id_product]': price.product_id.ps_id, 'limit': '1'})
                if response['specific_prices']:
                    #SP exist
                    price.ps_id = int(response['specific_prices']['specific_price']['attrs']['id'])
                    price.save()
                    return self.get_or_create_specific_price(price)
            price_data = self._api.get('specific_prices', options={'schema': 'blank'})
            price_data['specific_price']['id_product'] = price.product_id.ps_id
            #price_data['specific_price']['id_product_attribute'] = price.combination_id.ps_id
            price_data['specific_price']['id_product_attribute'] = 0
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
            response_add = self._api.add('specific_prices', price_data)
            price.ps_id = int(response_add['prestashop']['specific_price']['id'])

        price.updated = False
        price.save()

        if not response:
            response = self._api.get('specific_prices', resource_id=price.ps_id)
        return response

    def get_or_create_stock(self, stock):
        if stock.ps_id:
            try:
                response = self._api.get('stock_availables', resource_id=stock.ps_id)
                response['stock_available']['quantity'] = 0 if stock.icg_stock < 0 else stock.icg_stock
                response_edit = self._api.edit('stock_availables', response)
                stock.ps_stock = int(response_edit['prestashop']['stock_available']['quantity'])
            except prestapyt.prestapyt.PrestaShopWebServiceError:
                #No exist in PS anymore. Recreate
                stock.ps_id = 0
                stock.save()
                return self.get_or_create_stock(stock)

        elif stock.combination_id.discontinued or not stock.combination_id.ps_id: #or not stock.combination_id.product_id.visible_web:
            stock.updated = False
            stock.save()
            return False
        else:
            response = self._api.get('stock_availables', None,
                {'filter[id_product_attribute]': stock.combination_id.ps_id, 'limit': '1'})
            if response['stock_availables']:
                #Stock really exist
                stock.ps_id = int(response['stock_availables']['stock_available']['attrs']['id'])
                stock.save()
                return self.get_or_create_stock(stock)

            #No es pot crear stock_avaiables
            stock.combination_id.ps_id = 0
            stock.combination_id.updated = True
            stock.combination_id.save()
            stock.save()
            return False

            stock_data = self._api.get('stock_availables', options={'schema': 'blank'})
            stock_data['stock_available']['id_product'] = stock.combination_id.product_id.ps_id
            stock_data['stock_available']['id_product_attribute'] = stock.combination_id.ps_id
            stock_data['stock_available']['id_shop'] = 1
            stock_data['stock_available']['quantity'] = 0 if stock.icg_stock < 0 else stock.icg_stock

            response = self._api.add('stock_availables', stock_data)
            stock.ps_id = int(response['prestashop']['stock_available']['id'])
            stock.ps_stock = int(response['prestashop']['stock_available']['quantity'])

        stock.updated = False
        stock.save()
        return self._api.get('stock_availables', resource_id=stock.ps_id)

    def get_or_create_language(self, lang):
        if lang.ps_id:
            try:
                response = self._api.get('languages', resource_id=lang.ps_id)
            except prestapyt.prestapyt.PrestaShopWebServiceError:
                #No exist in PS anymore. Recreate
                lang.ps_id = 0
                lang.save()
                return self.get_or_create_language(lang)
        else:
            if lang.ps_name:
                response = self._api.get('languages', None,
                    {'filter[name]': lang.ps_name, 'limit': '1'})
                if response['languages']:
                    #Lang really exist
                    lang.ps_id = int(response['languages']['language']['attrs']['id'])
                    lang.save()
                    return self.get_or_create_language(lang)
            lang_data = self._api.get('languages', options={'schema': 'blank'})
            lang_data['language']['name'] = lang.ps_name
            lang_data['language']['iso_code'] = lang.ps_iso_code
            if lang.ps_locale:
                lang_data['language']['locale'] = lang.ps_locale
            else:
                lang_data['language'].pop('locale')
            if lang.ps_language_code:
                lang_data['language']['language_code'] = lang.ps_language_code
            else:
                lang_data['language'].pop('language_code')
            lang_data['language']['active'] = 1 if lang.ps_active else 0
            lang_data['language']['is_rtl'] = 1 if lang.ps_is_rtl else 0
            lang_data['language']['date_format_lite'] = lang.ps_date_format_lite
            lang_data['language']['date_format_full'] = lang.ps_date_format_full

            response = self._api.add('languages', lang_data)
            lang.ps_id = int(response['prestashop']['language']['id'])

        lang.updated = False
        lang.save()
        return self._api.get('languages', resource_id=lang.ps_id)

    def carregaNous(self):
        ps_exceptions = []
        ps_man = []
        updated_manufacturers = models.Manufacturer.objects.filter(updated = True).exclude(icg_name__isnull=True).exclude(icg_name__exact='')
        for man in updated_manufacturers:
            try:
                m = self.get_or_create_manufacturer(man)
                if m:
                    ps_man.append(m['manufacturer']['id'])
            except Exception as e:
                print("Exception with : " + str(man))
                print(e)
                ps_exceptions.append(man)
                continue

        ps_prod = []
        updated_products = models.Product.objects.filter(updated = True)
        for prod in updated_products:
            try:
                p = self.get_or_create_product(prod)
                if p:
                    ps_prod.append(p['product']['id'])
            except:
                print("Exception with : " + str(prod))
                ps_exceptions.append(prod)
                continue

        ps_po = []
        updated_product_options = models.ProductOption.objects.filter(updated = True)
        for po in updated_product_options:
            try:
                p = self.get_or_create_product_options(po)
                if p:
                    ps_po.append(p['product_option']['id'])
            except:
                print("Exception with : " + str(po))
                ps_exceptions.append(po)
                continue

        ps_pov = []
        updated_product_options_values = models.ProductOptionValue.objects.filter(updated = True)
        for pov in updated_product_options_values:
            try:
                p = self.get_or_create_product_option_value(pov)
                if p:
                    ps_pov.append(p['product_option_value']['id'])
            except:
                print("Exception with : " + str(pov))
                ps_exceptions.append(pov)
                continue

        ps_comb = []
        updated_comb = models.Combination.objects.filter(updated = True)
        for comb in updated_comb:
            try:
                c = self.get_or_create_combination(comb)
                if c:
                    ps_comb.append(c['combination']['id'])
            except Exception as e:
                print("Exception with : " + str(comb))
                print(type(e))
                print(e)
                ps_exceptions.append(comb)
                continue

        ps_price = []
        updated_price = models.Price.objects.filter(updated = True)
        for price in updated_price:
            try:
                c = self.get_or_create_price(price)
                if c:
                    ps_price.append(c['combination']['id'])
            except:
                print("Exception with: " + str(price))
                ps_exceptions.append(price)
                continue

        ps_sp = []
        updated_specific_price = models.SpecificPrice.objects.filter(updated = True)
        for sp in updated_specific_price:
            try:
                s = self.get_or_create_specific_price(sp)
                if s:
                    ps_sp.append(s['specific_price']['id'])
            except:
                print("Exception with: " + str(sp))
                ps_exceptions.append(sp)
                continue

        ps_stock = []
        updated_stock = models.Stock.objects.filter(updated = True)
        for stock in updated_stock:
            try:
                s = self.get_or_create_stock(stock)
                if s:
                    ps_stock.append(s['stock_available']['id'])
            except:
                print("Exception with: " + str(stock))
                ps_exceptions.append(stock)
                continue

        updated = (ps_sp or ps_price or ps_comb or ps_pov or ps_po or ps_prod or ps_man or ps_stock)
        return updated, {'ps_manufacturers': ps_man, 'ps_products': ps_prod, 'ps_productoptions': ps_po,
             'ps_productoptionvalues': ps_pov, 'ps_combinations': ps_comb, 'errors': ps_exceptions,
            'ps_specifiprices': ps_sp, 'ps_combinations_prices': ps_price, 'ps_stock': ps_stock}

# vim: et ts=4 sw=4
