from django.core.management.base import BaseCommand, CommandError
from djangodocker.simpleapp.prestashop import ControllerPrestashop
from djangodocker.simpleapp.controller import ControllerICGProducts
from djangodocker.simpleapp.models import *
import logging
from datetime import datetime

class Command(BaseCommand):
    help = 'Try to create new django objects from exisiting in Pestashop'


    def getPSDict(self, resource, ps_id):
        p = ControllerPrestashop()
        return p._api.get(resource, ps_id)


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

    def getProduct(self, ps_id):
        result_dj_prod = Product.objects.filter(ps_id = ps_id)
        if not result_dj_prod:
            prod_ps_dict = self.getPSDict('products',  ps_id)
            prod = Product.createFromPS(prod_ps_dict)
            prod.updateFromICG()
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
            comb = Combination.createFromPS(comb_ps_dict, prod)
            comb.updateFromICG()
            comb.save()
            pov_list = comb_ps_dict['combination']['associations']['product_option_values']['product_option_value']
            if isinstance(pov_list, list):
                pov1 = self.getProductOptionValue(pov_list[0]['id'], prod)
                pov2 = self.getProductOptionValue(pov_list[1]['id'], prod)
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
            stock.updateFromICG()
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
            prod = self.getProduct(sp_ps_dict['specific_price']['id_product'])
            sp = SpecificPrice.createFromPS(sp_ps_dict, prod)
            sp.updateFromICG()
            sp.save()
        else:
            sp = SpecificPrice.objects.get(pk=result_dj_sp[0].pk)

        return sp

    def handle(self, *args, **options):
        logger = logging.getLogger('command.createfromprestashop')
        p = ControllerPrestashop()
        stock_list = p._api.get('stock_availables', None, {'limit': 100})
        if stock_list['stock_availables']:
            if isinstance(stock_list['stock_availables']['stock_available'], list):
                for s in stock_list['stock_availables']['stock_available']:
                    stock = self.getStock(s['attrs']['id'])
            else:
                self.getStock(stock_list['stock_availables']['stock_available']['attrs']['id'])

        sp_list = p._api.get('specific_prices', None, {'limit': 100})
        if sp_list['specific_prices']:
            if isinstance(sp_list['specific_prices']['specific_price'], list):
                for sp in sp_list['specific_prices']['specific_price']:
                    special_price = self.getSpecificPrice(sp['attrs']['id'])
            else:
                self.getSpecificPrice(sp_list['specific_prices']['specific_price']['attrs']['id'])

