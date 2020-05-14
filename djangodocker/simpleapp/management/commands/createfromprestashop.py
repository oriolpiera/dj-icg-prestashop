from django.core.management.base import BaseCommand, CommandError
from djangodocker.simpleapp.prestashop import ControllerPrestashop
from djangodocker.simpleapp.controller import ControllerICGProducts
from djangodocker.simpleapp.models import *
import logging
from datetime import datetime

class Command(BaseCommand):
    help = 'Try to create new django objects from exisiting in Pestashop'
    c = None
    p = None

    def __init__(self):
        self.c = ControllerICGProducts()
        self.p = ControllerPrestashop()

    def getPSDict(self, resource, ps_id):
        return self.p._api.get(resource, ps_id)


    def getProductOption(self, ps_id, prod):
        result_dj_po1 = ProductOption.objects.filter(ps_id = ps_id)
        if not result_dj_po1:
            po1_ps_dict = self.getPSDict('product_options', ps_id)
            po1 = ProductOption.createFromPS(po1_ps_dict, prod)
            po1.save()
        else:
            po1 = ProductOption.objects.get(pk=result_dj_po1[0].pk)
        return po1

    def getProductOptionValue(self, ps_id, prod):
        result_dj_pov1 = ProductOptionValue.objects.filter(ps_id = ps_id)
        if not result_dj_pov1:
            pov1_ps_dict = self.getPSDict('product_option_values', ps_id)
            po1 = self.getProductOption(pov1_ps_dict['product_option_value']['id_attribute_group'], prod)
            pov1 = ProductOptionValue.createFromPS(pov1_ps_dict, po1)
            pov1.save()
        else:
            pov1 = ProductOptionValue.objects.get(pk=result_dj_pov1[0].pk)

        return pov1

    def getManufacturer(self, ps_id):
        result_dj_man = Manufacturer.objects.filter(ps_id = ps_id)
        if not result_dj_man:
            man_ps_dict = self.getPSDict('manufacturers',  ps_id)
            man = Manufacturer.createFromPS(man_ps_dict)
            man.save()
            self.c.updateManufacturerFromICG(man)
        else:
            man = Manufacturer.objects.get(pk=result_dj_man[0].pk)
        return man

    def getProduct(self, ps_id):
        result_dj_prod = Product.objects.filter(ps_id = ps_id)
        if not result_dj_prod:
            prod_ps_dict = self.getPSDict('products',  ps_id)
            man = self.getManufacturer(prod_ps_dict['product']['id_manufacturer'])
            prod = Product.createFromPS(prod_ps_dict)
            prod.manufacturer = man
            self.c.updateProductFromICG(prod)
            prod.save()
        else:
            prod = Product.objects.get(pk=result_dj_prod[0].pk)
        return prod

    def getCombination(self, ps_id):
        result_dj_comb = Combination.objects.filter(ps_id = ps_id)
        if not result_dj_comb:
            comb_ps_dict = self.getPSDict('combinations', ps_id)
            if  comb_ps_dict['combination']['id_product'] == '0':
                return False, False
            prod = self.getProduct(comb_ps_dict['combination']['id_product'])
            pov_list = comb_ps_dict['combination']['associations']['product_option_values']['product_option_value']
            if isinstance(pov_list, list):
                pov1 = self.getProductOptionValue(pov_list[0]['id'], prod)
                pov2 = self.getProductOptionValue(pov_list[1]['id'], prod)
            comb = Combination.createFromPS(comb_ps_dict, prod)
            if pov1.po_id.ps_icg_type == 'talla':
                comb.talla_id = pov1
                comb.icg_talla = pov1.ps_name
                comb.color_id = pov2
                comb.icg_color = pov2.ps_name
            else:
                comb.talla_id = pov2
                comb.icg_talla = pov2.ps_name
                comb.color_id = pov1
                comb.icg_color = pov1.ps_name
            comb.save()
            price = Price.createFromPS(comb_ps_dict, comb)
            price.save()
            self.c.updateCombinationFromICG(comb)
            self.c.updatePriceFromICG(price)
        else:
            comb = Combination.objects.get(pk=result_dj_comb[0].pk)
            prod = Product.objects.get(pk=comb.product_id.pk)

        return comb, prod

    def getStock(self, ps_id):
        result_dj_stock = Stock.objects.filter(ps_id = ps_id)
        if not result_dj_stock:
            stock_ps_dict = self.getPSDict('stock_availables', ps_id)
            if stock_ps_dict['stock_available']['id_product_attribute'] == '0':
                return False
            comb, prod = self.getCombination(stock_ps_dict['stock_available']['id_product_attribute'])
            if not comb or not prod:
                return False
            stock = Stock.createFromPS(stock_ps_dict, prod, comb)
            self.c.updateStockFromICG(stock)
            stock.save()
        else:
            stock = Stock.objects.get(pk=result_dj_stock[0].pk)

        return stock

    def getSpecificPrice(self, ps_id):
        result_dj_sp = SpecificPrice.objects.filter(ps_id = ps_id)
        if not result_dj_sp:
            sp_ps_dict = self.getPSDict('specific_prices', ps_id)
            if sp_ps_dict['specific_price']['id_product'] == '0':
                return False
            result_dj_prod = Product.objects.filter(ps_id = sp_ps_dict['specific_price']['id_product'])
            if not result_dj_prod:
                #If Product not exist, avoid SP creation because we don't have combination
                return False
            prod = self.getProduct(sp_ps_dict['specific_price']['id_product'])
            sp = SpecificPrice.createFromPS(sp_ps_dict, prod)
            self.c.updateSpecificPriceFromICG(sp)
            sp.save()
        else:
            sp = SpecificPrice.objects.get(pk=result_dj_sp[0].pk)

        return sp

    def add_arguments(self, parser):
        parser.add_argument('--limit', help='Num elements to download form PS')
        parser.add_argument('--offset', help='First element to download form PS')


    def handle(self, *args, **options):
        limit = ''
        if 'offset' in options:
            limit += options['offset'] + ','
        if 'limit' in options:
            limit += options['limit']

        logger = logging.getLogger('command.createfromprestashop')
        p = ControllerPrestashop()
        #stock_list = p._api.get('stock_availables', None, {'limit': limit})
        stock_list = {'stock_availables': False}
        if stock_list['stock_availables']:
            if isinstance(stock_list['stock_availables']['stock_available'], list):
                for s in stock_list['stock_availables']['stock_available']:
                    stock = self.getStock(s['attrs']['id'])
            else:
                self.getStock(stock_list['stock_availables']['stock_available']['attrs']['id'])

        sp_list = p._api.get('specific_prices', None, {'limit': limit})
        if sp_list['specific_prices']:
            if isinstance(sp_list['specific_prices']['specific_price'], list):
                for sp in sp_list['specific_prices']['specific_price']:
                    special_price = self.getSpecificPrice(sp['attrs']['id'])
            else:
                self.getSpecificPrice(sp_list['specific_prices']['specific_price']['attrs']['id'])

