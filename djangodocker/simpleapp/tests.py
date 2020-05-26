# -*- coding: utf-8 -*-
import factory
import pytest
from . import models, mssql, controller, prestashop, mytools, constants
import random
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
import prestapyt
import pandas as pd
from pandas._testing import assert_frame_equal
import os
from django.core.management import call_command
from djangodocker.simpleapp.management.commands.createfromprestashop import Command

class ManufacturerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.Manufacturer'
        django_get_or_create = ('icg_name','ps_name')

    icg_id = factory.Sequence(int)
    icg_name = factory.Sequence(lambda n: 'Company name %d' % n)
    ps_name = factory.Sequence(lambda n: 'Company name %d' % n)

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.Product'
        django_get_or_create = ('icg_name','ps_name', 'icg_id')

    icg_id = factory.Sequence(int)
    icg_reference = factory.Sequence(lambda n: 100000 + n)
    ps_name = factory.Sequence(lambda n: 'Product name %d' % n)
    manufacturer = factory.SubFactory(ManufacturerFactory)
    icg_name = factory.Sequence(lambda n: 'Product name %d' % n)

class CombinationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.Combination'
        django_get_or_create = ('icg_talla','icg_color', 'product_id')

    icg_talla = factory.Sequence(lambda n: "t_%d" % n)
    icg_color = factory.Sequence(lambda n: "c_%d" % n)
    product_id = factory.SubFactory(ProductFactory)
    ean13 = factory.Sequence(lambda n: str(1000000000000 + n))
    minimal_quantity = 1

class StockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.Stock'
        django_get_or_create = ('icg_stock','ps_stock')

    icg_stock = 0
    ps_stock = 0
    combination_id = factory.SubFactory(CombinationFactory)

class PriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.Price'
        django_get_or_create = ('pvp_siva', 'combination_id')

    pvp_siva = 0
    combination_id = factory.SubFactory(CombinationFactory)

class UserFactory(factory.django.DjangoModelFactory):
    email = 'admin@1admin.com'
    username = 'admin1'
    password = factory.PostGenerationMethodCall('set_password', 'adm1n1')
    is_superuser = True
    is_staff = True
    is_active = True

class ProductOptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.ProductOption'
        django_get_or_create = ('ps_icg_type', 'ps_id', 'ps_name')

    ps_id = factory.Sequence(lambda n: n)
    ps_icg_type = 'talla'
    product_id = factory.SubFactory(ProductFactory)
    ps_name = '0_talla'


class ProductOptionValueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.ProductOptionValue'
        django_get_or_create = ('icg_name', 'ps_id')

    ps_id = 0
    po_id = factory.SubFactory(ProductOptionFactory)
    icg_name = factory.Sequence(lambda n: "Attr_%d" % n)
    ps_name = icg_name

class SpecificPriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.SpecificPrice'
        django_get_or_create = ('ps_id', 'combination_id', 'dto_percent')

    ps_id = 0
    combination_id = factory.SubFactory(CombinationFactory)
    dto_percent = random.randint(1,50)

class LanguageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.Language'
        django_get_or_create = ('ps_id', 'ps_name', 'ps_iso_code')

    ps_id = 0
    ps_name = factory.Sequence(lambda n: "Lang_%d" % n)
    ps_iso_code = 'es'
    ps_date_format_lite = 'd/m/Y'
    ps_date_format_full = 'd/m/Y H:i:s'
    ps_is_rtl = 0


@pytest.mark.django_db
class TestSimpleApp:
    def test_one(self):
        x = "my simple app test"
        assert 'simple app' in x

    def test_createOneManufacturer_ok(self):
        ManufacturerFactory()
        man_list = models.Manufacturer.objects.all()
        assert len(man_list) is 1

    def test_createOneProduct_ok(self):
        ProductFactory()
        man_list = models.Product.objects.all()
        assert len(man_list) is 1

    def test_createOneCombination_ok(self):
        CombinationFactory()
        prod_list = models.Product.objects.all()
        comb_list = models.Combination.objects.all()
        assert len(prod_list) is 1
        assert len(comb_list) is 1

    def test_createOneStock_ok(self):
        StockFactory()
        man_list = models.Stock.objects.all()
        assert len(man_list) is 1

    def test_createOnePrice_ok(self):
        p = PriceFactory()
        comb_list = models.Combination.objects.all()
        price_list = models.Price.objects.all()
        assert len(comb_list) is 1
        assert len(price_list) is 1

    def test__updateFromICG_product(self):
        p = ProductFactory()
        p.icg_id = 7500
        p.icg_reference = '0930095'
        p.save()
        result = p.updateFromICG()
        assert result

        #Manufacturer not exist
        p = ProductFactory()
        p.icg_id = 7500
        p.icg_reference = '0930095'
        p.manufacturer = None
        p.save()
        result = p.updateFromICG()
        assert result
        assert p.manufacturer

    def test__updateFromICG_combination(self):
        c = CombinationFactory()
        c.updated = False
        c.product_id.icg_reference = '0930095'
        c.icg_talla = '12'
        c.icg_color = 'CAR 12 ML'
        c.save()
        result = c.updateFromICG()
        assert result
        assert c.updated

    def test__updateFromICG_stock(self):
        s  = StockFactory()
        s.updated = False
        s.combination_id.product_id.icg_id = 7500
        s.combination_id.icg_talla = '12'
        s.combination_id.icg_color = 'CAR 12 ML'
        s.save()
        result = s.updateFromICG()
        assert result
        assert s.updated

    def test__updateFromICG_price(self):
        c = CombinationFactory()
        c.product_id.icg_id = 7500
        c.icg_talla = '12'
        c.icg_color = 'CAR 12 ML'
        p = PriceFactory(combination_id = c)
        p.updated = False
        p.save()
        result = p.updateFromICG()
        assert result
        assert p.updated

    def test__createProductOptionValue(self):
        pov = ProductOptionValueFactory()
        pov.icg_name = ' {60 X 60}'
        pov.ps_name = ''
        pov.save()
        assert pov.ps_name == ' 60 X 60'


@pytest.mark.django_db
class TestControllerPrestashop:
    @classmethod
    def setup_class(self):
        self._api =  prestapyt.PrestaShopWebServiceDict(
            'http://prestashop/api', 'GENERATE_COMPLEX_KEY_LIKE_THIS!!', debug=True, verbose=True)
        self.p = prestashop.ControllerPrestashop()
        self.helper_clean_prestashop(self)

    def helper_clean_prestashop(self):
        self.helper_cleanPS_oneResource(self, 'product')
        self.helper_cleanPS_oneResource(self, 'manufacturer')
        self.helper_cleanPS_oneResource(self, 'combination')
        self.helper_cleanPS_oneResource(self, 'product_option')
        self.helper_cleanPS_oneResource(self, 'product_option_value')
        self.helper_cleanPS_oneResource(self, 'specific_price')
        #self.helper_cleanPS_oneResource(self, 'stock_available') API not allowed

    def helper_cleanPS_oneResource(self, resource_name, keep_one=False):
        resource_name_plural = resource_name + 's'
        resource_list = []
        response = self._api.get(resource_name_plural, None)
        if response[resource_name_plural]:
            if isinstance(response[resource_name_plural][resource_name], list):
                for p in  response[resource_name_plural][resource_name]:
                    resource_list.append(int(p['attrs']['id']))
            else:
                resource_list = [response[resource_name_plural][resource_name]['attrs']['id']]
            if keep_one and len(resource_list) > 1:
                self._api.delete(resource_name_plural, resource_ids=resource_list[1:])
            elif not keep_one:
                self._api.delete(resource_name_plural, resource_ids=resource_list)

    def test__get_or_create_manufacturer__ok(self):
        # Create one
        man = ManufacturerFactory()
        man_ps = self.p.get_or_create_manufacturer(man)
        assert man.ps_id
        assert man_ps['manufacturer']['id']

        # Get one
        man_ps1 = self.p.get_or_create_manufacturer(man)
        assert man_ps1['manufacturer'] == man_ps['manufacturer']

        # Update one
        man.icg_name = 'other_name'
        man_ps2 = self.p.get_or_create_manufacturer(man)
        assert man_ps1['manufacturer'] != man_ps2['manufacturer']
        assert man_ps2['manufacturer']['name'] == 'other_name'

        # Create other
        man1 = ManufacturerFactory()
        man_ps1 = self.p.get_or_create_manufacturer(man1)
        assert man1.ps_id
        assert man_ps1['manufacturer'] is not man_ps['manufacturer']


    def test__get_or_create_product__ok(self):
        # Create one
        prod = ProductFactory()
        prod_ps = self.p.get_or_create_product(prod)
        assert prod.ps_id
        assert prod_ps['product']['id']
        po_list = models.ProductOption.objects.all()
        assert len(po_list) is 2

        # No create
        prod1 = ProductFactory(visible_web=False)
        prod_ps1 = self.p.get_or_create_product(prod1)
        assert not prod1.ps_id
        assert prod_ps1 == {}

        # Get one
        prod_ps3 = self.p.get_or_create_product(prod)
        assert prod_ps['product'] == prod_ps3['product']

        # Create other
        prod2 = ProductFactory()
        prod_ps4 = self.p.get_or_create_product(prod2)
        assert prod.ps_id
        assert prod2.ps_id
        assert prod_ps['product'] != prod_ps4['product']
        po_list = models.ProductOption.objects.all()
        assert len(po_list) is 4

        # Update one
        prod.icg_reference = '1234'
        prod.manufacturer = ManufacturerFactory(ps_id = 2)
        prod.icg_name = 'Modify product name'
        prod.visible_web = False
        prod_ps5 = self.p.get_or_create_product(prod)
        assert prod_ps5['product']['id_manufacturer'] != prod_ps['product']['id_manufacturer']
        assert mytools.get_ps_language(prod_ps5['product']['name']['language']) == 'Modify product name'
        assert prod_ps5['product']['reference'] == '1234'
        assert prod_ps5['product']['active'] == '0'
        assert prod_ps5['product']['id'] == prod_ps['product']['id']


    def test__get_or_create_combination__ok(self):
        # Create one
        comb = CombinationFactory(icg_talla="12", icg_color="***", product_id__icg_id=7498)
        assert not comb.discontinued
        comb_ps1 = self.p.get_or_create_combination(comb)
        assert comb.ps_id
        comb_ps_id = comb.ps_id
        assert comb_ps1['combination']['id']
        po_list = models.ProductOption.objects.all()
        pov_list = models.ProductOptionValue.objects.all()
        assert len(po_list) is 2
        assert len(pov_list) is 2

        # Get one
        comb_ps2 = self.p.get_or_create_combination(comb)
        assert comb_ps1['combination']['id'] == comb_ps2['combination']['id']

        # Create other
        p2 = ProductFactory(icg_id=7499, ps_id=9)
        comb2 = CombinationFactory(icg_talla="24", icg_color="***", product_id = p2)
        comb_ps3 = self.p.get_or_create_combination(comb2)
        assert comb_ps1['combination']['id'] != comb_ps3['combination']['id']
        po_list = models.ProductOption.objects.all()
        pov_list = models.ProductOptionValue.objects.all()
        assert len(po_list) is 4
        assert len(pov_list) is 4

        #Delete one
        comb.discontinued = True
        comb_ps4 = self.p.get_or_create_combination(comb)
        assert comb_ps4 is True

        #Exeption when try to eliminate not existing combination
        comb.ps_id = comb_ps_id
        comb.save()
        with pytest.raises(prestapyt.prestapyt.PrestaShopWebServiceError):
            self.p.get_or_create_combination(comb)

        # Update one
        comb2.ean13 = '1234567890123'
        comb_ps5 = self.p.get_or_create_combination(comb2)
        assert comb_ps5['combination']['ean13'] != comb_ps3['combination']['ean13']
        assert comb_ps5['combination']['id'] == comb_ps3['combination']['id']

        #No create discontinued
        p3 = ProductFactory(icg_id=8001, ps_id=19)
        comb3 = CombinationFactory(icg_talla="24", icg_color="***", product_id = p3)
        comb3.discontinued = True
        comb_ps4 = self.p.get_or_create_combination(comb3)
        assert comb_ps4 is None

        #Error when ean13 is an space
        comb3 = CombinationFactory(icg_talla="14", icg_color="***", product_id = p3)
        comb3.ean13 = ' '
        comb3.save()
        comb_ps5 = self.p.get_or_create_combination(comb3)
        assert comb_ps5['combination']['id']

    def test__get_or_create_product_options__ok(self):
        # Create one
        p1 = ProductFactory()
        po = ProductOptionFactory(product_id = p1)
        po_ps1 = self.p.get_or_create_product_options(po)
        assert po.ps_id
        assert po_ps1['product_option']['id']

        # Get one
        po_ps2 = self.p.get_or_create_product_options(po)
        assert po_ps1['product_option']['id'] == po_ps2['product_option']['id']

        # Create other
        p2 = ProductFactory()
        p2.ps_id = 9999
        p2.save()
        po2 = ProductOptionFactory(ps_id = 0, ps_name='9999_talla', product_id = p2)
        po_ps3 = self.p.get_or_create_product_options(po2)
        assert po_ps3['product_option']['id'] != po_ps2['product_option']['id']


    def test__get_or_create_product_option_value__ok(self):
        # Create one
        po = ProductOptionFactory()
        po_ps1 = self.p.get_or_create_product_options(po)
        pov = ProductOptionValueFactory(po_id = po)
        pov_ps1 = self.p.get_or_create_product_option_value(pov)
        assert pov.ps_id
        assert pov_ps1['product_option_value']['id']

        # Get one
        pov_ps2 = self.p.get_or_create_product_option_value(pov)
        assert pov_ps1['product_option_value']['id'] == pov_ps2['product_option_value']['id']

        # Create other
        pov2 = ProductOptionValueFactory()
        pov_ps3 = self.p.get_or_create_product_option_value(pov2)
        assert pov_ps3['product_option_value']['id'] != pov_ps2['product_option_value']['id']

        # No create other when existing in PS but we don't have no ps_id
        pov2.ps_id = 0
        pov2.save()
        pov_ps4 = self.p.get_or_create_product_option_value(pov2)
        assert pov_ps3['product_option_value']['id'] == pov_ps4['product_option_value']['id']

        # Create one special chars
        po = ProductOptionFactory()
        po.save()
        po_ps1 = self.p.get_or_create_product_options(po)
        pov = ProductOptionValueFactory(po_id = po, icg_name = '{60X60}', ps_name='')
        pov.save()
        pov_ps1 = self.p.get_or_create_product_option_value(pov)
        assert pov.ps_id
        assert pov_ps1['product_option_value']['id']
        assert mytools.get_ps_language(pov_ps1['product_option_value']['name']['language']) == '60X60'
        assert pov.ps_name == '60X60'

    def test__get_or_create_price_ok(self):
        # Create one
        comb = CombinationFactory()
        comb_ps1 = self.p.get_or_create_combination(comb)
        p1 = PriceFactory(combination_id = comb, pvp_siva = 10.5)
        p_ps1 = self.p.get_or_create_price(p1)
        assert p1.ps_id
        assert float(p_ps1['combination']['price']) == 10.5

        # Get one
        p_ps2 = self.p.get_or_create_price(p1)
        assert p_ps1['combination']['id'] == p_ps2['combination']['id']

        # Create other
        prod1 = ProductFactory(icg_id=7499, ps_id=9)
        comb2 = CombinationFactory(icg_talla="24", icg_color="***", product_id = prod1)
        p2 = PriceFactory(combination_id = comb2, pvp_siva = 20.59)
        p_ps3 = self.p.get_or_create_price(p2)
        assert p_ps1['combination']['id'] != p_ps3['combination']['id']

        # Update one
        p2.pvp_siva = 19.99
        p_ps5 = self.p.get_or_create_price(p2)
        assert p_ps5['combination']['price'] != p_ps3['combination']['price']
        assert p_ps5['combination']['id'] == p_ps3['combination']['id']


    def test__get_or_create_stock_ok(self):
        # Create one
        comb = CombinationFactory()
        comb_ps1 = self.p.get_or_create_combination(comb)
        s = StockFactory(combination_id = comb, icg_stock = 10)
        s_ps1 = self.p.get_or_create_stock(s)
        assert s.ps_id
        assert s_ps1['stock_available']['quantity'] == '10'
        assert s.icg_stock == s.ps_stock

        # Get one
        s_ps2 = self.p.get_or_create_stock(s)
        assert s_ps1['stock_available']['id'] == s_ps2['stock_available']['id']

        # Create other
        p2 = ProductFactory(icg_id=7499, ps_id = 9)
        comb2 = CombinationFactory(product_id = p2)
        comb_ps2 = self.p.get_or_create_combination(comb2)
        s2 = StockFactory(combination_id = comb2, icg_stock = 12)
        s_ps3 = self.p.get_or_create_stock(s2)
        assert s_ps1['stock_available']['id'] != s_ps3['stock_available']['id']
        s.ps_id != s2.ps_id

        # Update one
        s2.icg_stock = 6
        s_ps4 = self.p.get_or_create_stock(s2)
        assert s_ps4['stock_available']['id'] == s_ps3['stock_available']['id']
        assert s_ps4['stock_available']['quantity'] == '6'
        assert s2.icg_stock == s2.ps_stock

        # No delete
        s2.icg_stock = 0
        s_ps5 = self.p.get_or_create_stock(s2)
        assert s2.ps_id

        # Create negative
        p3 = ProductFactory(icg_id=7399, ps_id = 11)
        comb3 = CombinationFactory(product_id = p3)
        comb_ps3 = self.p.get_or_create_combination(comb3)
        s3 = StockFactory(combination_id = comb3, icg_stock = -10)
        s_ps6 = self.p.get_or_create_stock(s3)
        assert s_ps6['stock_available']['quantity'] == '0'

        # Update one negative
        s2.icg_stock = -6
        s_ps4 = self.p.get_or_create_stock(s2)
        assert s_ps4['stock_available']['quantity'] == '0'


    def test__get_or_create_specific_price__ok(self):
        # Create one
        comb = CombinationFactory()
        comb_ps1 = self.p.get_or_create_combination(comb)
        sp1 = SpecificPriceFactory(combination_id = comb)
        sp_ps1 = self.p.get_or_create_specific_price(sp1)
        assert sp1.ps_id
        assert sp_ps1['specific_price']['id']

        # Get one
        sp_ps2 = self.p.get_or_create_specific_price(sp1)
        assert sp_ps1['specific_price']['id'] == sp_ps2['specific_price']['id']

        # Create other
        p2 = ProductFactory(icg_id=7499, ps_id=9)
        comb2 = CombinationFactory(product_id = p2)
        sp2 = SpecificPriceFactory(combination_id = comb2)
        comb_ps3 = self.p.get_or_create_combination(comb2)
        sp_ps3 = self.p.get_or_create_specific_price(sp2)
        assert sp_ps1['specific_price']['id'] != sp_ps3['specific_price']['id']
        sp2_ps_id = sp2.ps_id

        # Update one
        sp2.dto_percent = 10
        sp_ps4 = self.p.get_or_create_specific_price(sp2)
        assert sp_ps4['specific_price']['id'] == sp_ps3['specific_price']['id']
        assert float(sp_ps4['specific_price']['reduction']) == 0.1

        # Delete one
        sp2.dto_percent = 0
        sp_ps5 = self.p.get_or_create_specific_price(sp2)
        assert not sp2.ps_id

        #Exeption when try to eliminate not existing specific price
        sp2.ps_id = sp2_ps_id
        with pytest.raises(prestapyt.prestapyt.PrestaShopWebServiceError):
            self.p.get_or_create_specific_price(sp2)

    def test__get_or_create_product_options_django__ok(self):
        # Create two
        prod = ProductFactory()
        prod_dj1 = self.p.get_or_create_product_options_django(prod, 'talla')
        prod_dj2 = self.p.get_or_create_product_options_django(prod, 'color')
        assert len(models.ProductOption.objects.all()) is 2
        assert len(models.ProductOption.objects.filter(updated = True)) is 2

        # Get two
        prod_dj1 = self.p.get_or_create_product_options_django(prod, 'talla')
        prod_dj2 = self.p.get_or_create_product_options_django(prod, 'color')
        assert len(models.ProductOption.objects.all()) is 2
        assert len(models.ProductOption.objects.filter(updated = True)) is 2


    def test__get_or_create_language__ok(self):
        self.helper_cleanPS_oneResource('language', keep_one=True)

        # Create one
        lang = LanguageFactory()
        lang_ps = self.p.get_or_create_language(lang)
        assert lang.ps_id
        assert lang_ps['language']['id']

        # Get one
        lang_ps1 = self.p.get_or_create_language(lang)
        assert lang_ps1['language'] == lang_ps['language']

        # Create other
        lang1 = LanguageFactory()
        lang_ps1 = self.p.get_or_create_language(lang1)
        assert lang1.ps_id
        assert lang_ps1['language'] is not lang_ps['language']

        self.helper_cleanPS_oneResource('language', keep_one=True)


    def test__filterProductsReference__ok(self):
        prod = ProductFactory()
        prod_ps = self.p.get_or_create_product(prod)
        response = self._api.get('products', None, {'filter[reference]': prod.icg_reference, 'limit': '1'})
        assert prod_ps['product']['id']  == response['products']['product']['attrs']['id']

    def test__carregaNous__ok(self):
        sp = SpecificPriceFactory.create_batch(2)
        price = PriceFactory.create_batch(2)
        assert len(models.Product.objects.all()) is 4
        assert len(models.Product.objects.filter(updated = True)) is 4
        assert len(models.ProductOption.objects.all()) is 0
        assert len(models.ProductOption.objects.filter(updated = True)) is 0
        assert len(models.Combination.objects.filter(updated = True)) is 4
        assert len(models.SpecificPrice.objects.filter(updated = True)) is 2
        assert len(models.Price.objects.filter(updated = True)) is 2
        assert len(models.ProductOptionValue.objects.filter(updated = True)) is 0

        updated, created = self.p.carregaNous()

        assert len(models.Manufacturer.objects.filter(updated = True)) is 0
        assert len(models.Manufacturer.objects.exclude(ps_id = 0)) is 4
        assert len(models.Product.objects.filter(updated = True)) is 0
        assert len(models.Product.objects.exclude(ps_id = 0)) is 4
        assert len(models.ProductOption.objects.filter(updated = True)) is 0
        assert len(models.ProductOption.objects.exclude(ps_id = 0)) is 8
        assert len(models.ProductOptionValue.objects.exclude(ps_id = 0)) is 8
        assert len(models.ProductOptionValue.objects.filter(updated = True)) is 0
        assert len(models.Combination.objects.exclude(ps_id = 0)) is 4
        assert len(models.Combination.objects.filter(updated = True)) is 0
        assert len(models.SpecificPrice.objects.filter(updated = True)) is 0
        assert len(models.SpecificPrice.objects.exclude(ps_id = 0)) is 2
        assert len(models.Price.objects.filter(updated = True)) is 0
        assert len(models.Price.objects.exclude(ps_id = 0)) is 2

        assert updated
        assert len(created['ps_manufacturers']) is 4
        assert len(created['ps_products']) is 4
        assert len(created['ps_productoptions']) is 8
        assert len(created['ps_productoptionvalues']) is 0
        assert len(created['ps_combinations']) is 4
        assert len(created['ps_specifiprices']) is 2
        assert len(created['ps_combinations_prices']) is 2

        for n in  created['ps_manufacturers']:
            assert self._api.get('manufacturers', n)
        for n in  created['ps_products']:
            assert self._api.get('products', n)
        for n in  created['ps_productoptions']:
            assert self._api.get('product_options', n)
        for n in  created['ps_productoptionvalues']:
            assert self._api.get('product_option_values', n)
        for n in created['ps_combinations']:
            assert self._api.get('combinations', n)
        for n in created['ps_specifiprices']:
            assert self._api.get('specific_prices', n)

        updated2, created2 = self.p.carregaNous()

        assert not updated2
        assert len(created2['ps_manufacturers']) is 0
        assert len(created2['ps_products']) is 0
        assert len(created2['ps_productoptions']) is 0
        assert len(created2['ps_productoptionvalues']) is 0
        assert len(created2['ps_combinations']) is 0
        assert len(created2['ps_specifiprices']) is 0
        assert len(created2['ps_combinations_prices']) is 0


    def test_createFromPS_Manufacturer(self):
        man = ManufacturerFactory()
        man_ps = self.p.get_or_create_manufacturer(man)
        man.delete()
        man2 = models.Manufacturer.createFromPS(man_ps)
        man2.save()
        assert man2.ps_name == man_ps['manufacturer']['name']
        assert man2.ps_id == man_ps['manufacturer']['id']
        assert len(models.Manufacturer.objects.all()) == 1

    def test_createFromPS_Product(self):
        prod = ProductFactory()
        prod_ps = self.p.get_or_create_product(prod)
        prod.delete()
        assert len(models.Product.objects.all()) == 0
        prod2 = models.Product.createFromPS(prod_ps)
        prod2.save()
        assert prod2.icg_reference == prod_ps['product']['reference']
        assert prod2.ps_id == prod_ps['product']['id']
        assert len(models.Product.objects.all()) == 1

        #Translation
        tp = models.TranslationProduct.objects.filter(prod = prod2)[0]
        tp.ps_name = 'Product name 0'
        assert len(models.TranslationProduct.objects.all()) == 1

    def test_updateTranslationFields_Product(self):
        prod = ProductFactory()
        prod.updateTranslationFields({'0': 'Field text'}, 'ps_name')
        assert len(models.TranslationProduct.objects.filter(prod=prod)) == 1
        tp = models.TranslationProduct.objects.filter(prod=prod)[0]
        assert tp.ps_name == 'Field text'

        #More than one language
        prod.updateTranslationFields({'0': 'Desc lang 0', '1': 'Desc lang 1'}, 'ps_description')
        assert len(models.TranslationProduct.objects.filter(prod=prod)) == 2
        tp = models.TranslationProduct.objects.filter(prod=prod)[0]
        assert tp.ps_name == 'Field text'
        assert tp.ps_description == 'Desc lang 0'

    def test_createFromPS_Combination(self):
        prod2 = ProductFactory()
        comb = CombinationFactory(product_id = prod2)
        comb_ps = self.p.get_or_create_combination(comb)
        comb.delete()
        assert len(models.Combination.objects.all()) == 0
        comb2 = models.Combination.createFromPS(comb_ps, prod2)
        comb2.save()
        assert comb2.ean13 == comb_ps['combination']['ean13']
        assert comb2.ps_id == comb_ps['combination']['id']
        assert len(models.Combination.objects.all()) == 1

    def test_createFromPS_Stock(self):
        prod2 = ProductFactory()
        comb2 = CombinationFactory(product_id = prod2)
        stock = StockFactory(combination_id = comb2)
        stock_ps = self.p.get_or_create_stock(stock)
        stock.delete()
        assert len(models.Stock.objects.all()) == 0
        stock2 = models.Stock.createFromPS(stock_ps, prod2, comb2)
        stock2.save()
        assert stock2.ps_stock == stock_ps['stock_available']['quantity']
        assert stock2.ps_id == stock_ps['stock_available']['id']
        assert len(models.Stock.objects.all()) == 1

    def test_createFromPS_Price(self):
        comb = CombinationFactory()
        comb_ps1 = self.p.get_or_create_combination(comb)
        p1 = PriceFactory(combination_id = comb, pvp_siva = 10.5)
        p_ps1 = self.p.get_or_create_price(p1)
        p1.delete()
        assert len(models.Price.objects.all()) == 0
        price2 = models.Price.createFromPS(p_ps1, comb)
        price2.save()
        assert price2.pvp_siva == float(p_ps1['combination']['price'])
        assert price2.ps_id == p_ps1['combination']['id']
        assert len(models.Price.objects.all()) == 1

    def test_createFromPS_ProductOption(self):
        p1 = ProductFactory()
        po = ProductOptionFactory(product_id = p1)
        po_ps1 = self.p.get_or_create_product_options(po)
        po.delete()
        assert len(models.ProductOption.objects.all()) == 0
        po2 = models.ProductOption.createFromPS(po_ps1, p1)
        po2.save()
        assert po2.ps_name == mytools.get_ps_language(po_ps1['product_option']['name']['language'])
        assert len(models.ProductOption.objects.all()) == 1

    def test_createFromPS_ProductOptionValue(self):
        po = ProductOptionFactory()
        po_ps1 = self.p.get_or_create_product_options(po)
        pov = ProductOptionValueFactory(po_id = po)
        pov_ps1 = self.p.get_or_create_product_option_value(pov)
        pov.delete()
        assert len(models.ProductOptionValue.objects.all()) == 0
        pov2 = models.ProductOptionValue.createFromPS(pov_ps1, po)
        pov2.save()
        assert pov2.ps_id == pov_ps1['product_option_value']['id']
        assert pov2.ps_name == mytools.get_ps_language(
            pov_ps1['product_option_value']['name']['language'])
        assert len(models.ProductOptionValue.objects.all()) == 1

    def test_createFromPS_SpecificPrice(self):
        comb = CombinationFactory()
        comb_ps1 = self.p.get_or_create_combination(comb)
        sp1 = SpecificPriceFactory(combination_id = comb)
        sp_ps1 = self.p.get_or_create_specific_price(sp1)
        sp1.delete()
        assert len(models.SpecificPrice.objects.all()) == 0
        sp2 = models.SpecificPrice.createFromPS(sp_ps1, comb.product_id)
        sp2.save()
        assert sp2.ps_id == sp_ps1['specific_price']['id']
        assert sp2.dto_percent == float(sp_ps1['specific_price']['reduction']) * 100
        assert len(models.SpecificPrice.objects.all()) == 1


    def test_Command_getProductOption(self):
        prod = ProductFactory()
        po = ProductOptionFactory(product_id = prod)
        po_ps = self.p.get_or_create_product_options(po)
        po.delete()
        c = Command()
        po2 = c.getProductOption(po_ps['product_option']['id'], prod)
        assert len(models.ProductOption.objects.all()) == 1
        assert po2.ps_name == mytools.get_ps_language(po_ps['product_option']['name']['language'])

    def test_Command_getProductOptionValue(self):
        prod = ProductFactory()
        po = ProductOptionFactory(product_id = prod)
        pov = ProductOptionValueFactory(po_id = po)
        pov_ps = self.p.get_or_create_product_option_value(pov)
        pov.delete()
        c = Command()
        pov2 = c.getProductOptionValue(pov_ps['product_option_value']['id'], prod)
        assert len(models.ProductOptionValue.objects.all()) == 1
        assert pov2.ps_name == mytools.get_ps_language(pov_ps['product_option_value']['name']['language'])

    def test_Command_getProduct(self):
        prod = ProductFactory()
        prod_ps = self.p.get_or_create_product(prod)
        prod.delete()
        c = Command()
        assert len(models.Product.objects.all()) == 0
        prod2 = c.getProduct(prod_ps['product']['id'])
        assert len(models.Product.objects.all()) == 1
        assert prod.ps_name == mytools.get_ps_language(prod_ps['product']['name']['language'])

    def test_Command_getCombination(self):
        prod = ProductFactory()
        prod_ps = self.p.get_or_create_product(prod)
        comb = CombinationFactory(product_id = prod)
        comb_ps = self.p.get_or_create_combination(comb)
        comb.delete()
        c = Command()
        assert len(models.Combination.objects.all()) == 0
        comb2, prod = c.getCombination(comb_ps['combination']['id'])
        assert len(models.Combination.objects.all()) == 1

    def test_Command_getStock(self):
        prod = ProductFactory()
        prod_ps = self.p.get_or_create_product(prod)
        comb = CombinationFactory(product_id = prod)
        comb_ps = self.p.get_or_create_combination(comb)
        stock = StockFactory(combination_id = comb)
        stock_ps = self.p.get_or_create_stock(stock)
        stock.delete()
        c = Command()
        assert len(models.Stock.objects.all()) == 0
        stock2 = c.getStock(stock_ps['stock_available']['id'])
        assert len(models.Stock.objects.all()) == 1

    def test_Command_getSpecificPrice(self):
        prod = ProductFactory()
        prod_ps = self.p.get_or_create_product(prod)
        comb = CombinationFactory(product_id = prod)
        comb_ps = self.p.get_or_create_combination(comb)
        sp = SpecificPriceFactory(combination_id = comb)
        sp_ps = self.p.get_or_create_specific_price(sp)
        sp.delete()
        c = Command()
        assert len(models.SpecificPrice.objects.all()) == 0
        sp2 = c.getSpecificPrice(sp_ps['specific_price']['id'])
        assert len(models.SpecificPrice.objects.all()) == 1

    @pytest.mark.skip('No way')
    def test_Command_createFromPrestashop(self):
        prod = ProductFactory()
        prod_ps = self.p.get_or_create_product(prod)
        comb = CombinationFactory(product_id = prod)
        comb_ps = self.p.get_or_create_combination(comb)
        stock = StockFactory(combination_id = comb)
        stock_ps = self.p.get_or_create_stock(stock)
        stock.delete()
        sp = SpecificPriceFactory(combination_id = comb)
        sp_ps = self.p.get_or_create_specific_price(sp)
        sp.delete()

        args = []
        opts = {}
        c = Command()
        c.handle(*args, **opts)

        assert len(models.Product.objects.all()) == 1
        assert len(models.ProductOption.objects.all()) == 2
        assert len(models.ProductOptionValue.objects.all()) == 2
        assert len(models.SpecificPrice.objects.all()) == 1
        assert len(models.Stock.objects.all()) == 1


@pytest.mark.django_db
class TestControllerICGProducts:
    @classmethod
    def setup_class(self):
        self.c = controller.ControllerICGProducts()

    def test_saveNewProducts(self):
        self.c.saveNewProducts()

        prod_list = models.Product.objects.all()
        man_list = models.Manufacturer.objects.all()
        comb_list = models.Combination.objects.all()
        po_list = models.ProductOption.objects.all()
        assert len(prod_list) is 6
        assert len(man_list) is 4
        assert len(comb_list) is 10

    def test_saveNewPrices(self):
        self.c.saveNewPrices()

        prod_list = models.Product.objects.all()
        man_list = models.Manufacturer.objects.all()
        comb_list = models.Combination.objects.all()
        sp_list = models.SpecificPrice.objects.all()
        price_list = models.Price.objects.all()
        assert len(prod_list) is 6
        assert len(comb_list) is 11
        assert len(sp_list) is 10
        assert len(price_list) is 11
        for p in prod_list:
            assert int(p.icg_reference)


    def test_saveNewStocks(self):
        self.c.saveNewStocks()

        prod_list = models.Product.objects.all()
        comb_list = models.Combination.objects.all()
        stock_list = models.Stock.objects.all()
        assert len(prod_list) is 8
        assert len(comb_list) is 10
        assert len(stock_list) is 10
        for p in prod_list:
            assert int(p.icg_reference)

    def test_get_create_or_update_ManufacturersOk(self):
        # Create one
        man1 = self.c.get_create_or_update('Manufacturer',
            {'icg_id': 14000},{'icg_name': 'ARTECREATION'})
        man_list = models.Manufacturer.objects.all()
        assert len(man_list) is 1

        # Get one
        man2 = self.c.get_create_or_update('Manufacturer',
            {'icg_id': 14000},{'icg_name': 'ARTECREATION'})
        man_list = models.Manufacturer.objects.all()
        assert len(man_list) is 1
        assert man1.pk is man2.pk

        # Update one
        assert man1.updated
        man1.updated = False
        man1.save()
        man3 = self.c.get_create_or_update('Manufacturer',
            {'icg_id': 14000},{'icg_name': 'artcreation'})
        man_list = models.Manufacturer.objects.all()
        assert len(man_list) is 1
        assert man1.pk is man3.pk
        man = models.Manufacturer.objects.get(icg_id = 14000)
        assert man.icg_name == "artcreation"
        assert man.updated
        assert man.fields_updated == "{'icg_name': 'artcreation'}"

        # Creates other
        man4 = self.c.get_create_or_update('Manufacturer',
            {'icg_id': 15000},{'icg_name': 'COBRA'})
        man_list = models.Manufacturer.objects.all()
        assert len(man_list) is 2
        assert man1.pk is not man4.pk


    def test_get_create_or_update_ProductOk(self):
        # Create one
        man = ManufacturerFactory()
        prod1 = self.c.get_create_or_update('Product', {'icg_id': 7500},
            {'icg_reference': '0930095', 'icg_name': 'Caja Tempera ArtCreation',
             'visible_web': True, 'manufacturer': man})
        prod_list = models.Product.objects.all()
        assert len(prod_list) is 1

        # Get one
        prod2 = self.c.get_create_or_update('Product', {'icg_id': 7500},
            {'icg_reference': '0930095', 'icg_name': 'Caja Témpera ArtCreation',
             'visible_web': True, 'manufacturer': man})
        prod_list = models.Product.objects.all()
        assert len(prod_list) is 1
        assert prod1.pk is prod2.pk

        # Get one without extra params
        prod2 = self.c.get_create_or_update('Product', {'icg_id': 7500}, {})
        prod_list = models.Product.objects.all()
        assert len(prod_list) is 1
        assert prod1.pk is prod2.pk
        assert prod2.icg_name == 'Caja Témpera ArtCreation'
        assert prod2.icg_reference == '0930095'

        # Update one
        assert prod1.updated
        prod1.updated = False
        prod1.save()
        assert not prod1.updated
        prod3 = self.c.get_create_or_update('Product', {'icg_id': 7500},
            {'icg_reference': '0930096', 'icg_name': 'Caja Témpera ArteCreation',
             'visible_web': False, 'manufacturer': man})
        prod_list = models.Product.objects.all()
        assert len(prod_list) is 1
        assert prod1.pk is prod3.pk
        prod = models.Product.objects.get(icg_id = 7500)
        assert prod.icg_name == 'Caja Témpera ArteCreation'
        assert prod.updated
        assert not prod.visible_web
        assert prod.fields_updated == "{'icg_name': 'Caja Témpera ArteCreation', 'icg_reference': '0930096', 'visible_web': '0'}"

        # Creates other
        prod4 = self.c.get_create_or_update('Product', {'icg_id': 7501},
            {'icg_reference': '0930099', 'icg_name': 'Óleo Cobra',
             'visible_web': True, 'manufacturer': man})
        prod_list = models.Product.objects.all()
        assert len(prod_list) is 2

    def test_get_create_or_update_ProductOptionOk(self):
        # Create two
        prod = ProductFactory(ps_id = 5)
        po1 = self.c.get_create_or_update('ProductOption',
            {'ps_name' : str(str(prod.ps_id) + "_" + "talla"), 'product_id': prod}, {})
        po2 = self.c.get_create_or_update('ProductOption',
            {'ps_name' : str(str(prod.ps_id) + "_" + "color"), 'product_id': prod}, {})
        po_list = models.ProductOption.objects.all()
        assert len(po_list) is 2

        # Create two Get two
        po3 = self.c.get_create_or_update('ProductOption',
            {'ps_name' : str(str(prod.ps_id) + "_" + "talla"), 'product_id': prod}, {})
        po4 = self.c.get_create_or_update('ProductOption',
            {'ps_name' : str(str(prod.ps_id) + "_" + "color"), 'product_id': prod}, {})
        po_list = models.ProductOption.objects.all()
        assert len(po_list) is 2
        assert po1.pk is po3.pk
        assert po2.pk is po4.pk

        # Creates others
        prod = ProductFactory(ps_id = 6)
        po5 = self.c.get_create_or_update('ProductOption',
            {'ps_name' : str(str(prod.ps_id) + "_" + "talla"), 'product_id': prod}, {})
        po6 = self.c.get_create_or_update('ProductOption',
            {'ps_name' : str(str(prod.ps_id) + "_" + "color"), 'product_id': prod}, {})
        po_list = models.ProductOption.objects.all()
        assert len(po_list) is 4

    def test_get_create_or_update_ProductOptionValueOk(self):
        # Create One
        po = ProductOptionFactory()
        pov1 = self.c.get_create_or_update('ProductOptionValue',
            {'po_id' : po, 'icg_name': '12 ML'}, {})
        pov_list = models.ProductOptionValue.objects.all()
        assert len(pov_list) is 1

        # Create two Get two
        pov2 = self.c.get_create_or_update('ProductOptionValue',
            {'po_id' : po, 'icg_name': '12 ML'}, {})
        pov_list = models.ProductOptionValue.objects.all()
        assert len(pov_list) is 1
        assert pov1.pk is pov2.pk

        # Creates other
        pov3 = self.c.get_create_or_update('ProductOptionValue',
            {'po_id' : po, 'icg_name': '120 ML'}, {})
        pov_list = models.ProductOptionValue.objects.all()
        assert len(pov_list) is 2

    def test_get_create_or_update_CombinationOk(self):
        # Create One
        prod = ProductFactory()
        comb1 = self.c.get_create_or_update('Combination', {'product_id': prod, 'icg_talla': '12',
            'icg_color': '12 ML'}, {'discontinued': False, 'ean13': '8712079332730'})
        comb_list = models.Combination.objects.all()
        assert len(comb_list) is 1

        # Get one
        comb2 = self.c.get_create_or_update('Combination', {'product_id': prod, 'icg_talla': '12',
            'icg_color': '12 ML'}, {'discontinued': False, 'ean13': '8712079332730'})
        comb_list = models.Combination.objects.all()
        assert len(comb_list) is 1
        assert comb1.pk is comb2.pk

        # Update one
        comb3 = self.c.get_create_or_update('Combination', {'product_id': prod, 'icg_talla': '12',
            'icg_color': '12 ML'}, {'discontinued': True, 'ean13': '8712079332734'})
        comb_list = models.Combination.objects.all()
        comb = models.Combination.objects.get(icg_color = "12 ML", icg_talla="12", product_id = prod )
        assert len(comb_list) is 1
        assert comb1.pk is comb3.pk
        assert comb.ean13 == "8712079332734"
        assert comb.discontinued
        assert comb.fields_updated == "{'ean13': '8712079332734', 'discontinued': True}"

        # Creates other
        comb4 = self.c.get_create_or_update('Combination', {'product_id': prod, 'icg_talla': '12',
            'icg_color': '120 ML'}, {'discontinued': True, 'ean13': '8712079332734'})
        comb_list = models.Combination.objects.all()
        assert len(comb_list) is 2
        assert comb1.pk is not comb4.pk



    def test_get_create_or_update_SpecificPriceOk(self):
        # Create One
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)
        sp1 = self.c.get_create_or_update('SpecificPrice', {'combination_id': comb},
            {'dto_percent': 20})
        sp_list = models.SpecificPrice.objects.all()
        assert len(sp_list) == 1
        assert sp1.dto_percent == 20

        # Get one
        sp2 = self.c.get_create_or_update('SpecificPrice', {'combination_id': comb},
            {'dto_percent': 20})
        sp_list = models.SpecificPrice.objects.all()
        assert len(sp_list) is 1
        assert sp1.pk is sp2.pk

        # Update one
        sp3 = self.c.get_create_or_update('SpecificPrice', {'combination_id': comb},
            {'dto_percent': 30})
        sp_list = models.SpecificPrice.objects.all()
        sp4 =  models.SpecificPrice.objects.get(pk=sp1.pk)
        assert len(sp_list) is 1
        assert sp1.pk is sp3.pk
        assert sp4.fields_updated == "{'dto_percent': 30}"
        assert sp4.dto_percent == 30

        # Creates other
        prod6 = ProductFactory(icg_id = 7503)
        comb2 = CombinationFactory(icg_talla="S.150ML", icg_color="***", product_id=prod6)
        sp5 = self.c.get_create_or_update('SpecificPrice', {'combination_id': comb2},
            {'dto_percent': 10})
        sp_list = models.SpecificPrice.objects.all()
        assert len(sp_list) is 2
        assert sp5.pk is not sp1.pk

    def test_get_create_or_update_StockOk(self):
        # Create one
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)
        stock = self.c.get_create_or_update('Stock', {'combination_id': comb}, {'icg_stock': 15})
        stock_list = models.Stock.objects.all()
        assert len(stock_list) is 1
        assert stock.icg_stock == 15

        # Get one
        stock2 = self.c.get_create_or_update('Stock', {'combination_id': comb}, {})
        stock_list = models.Stock.objects.all()
        assert len(stock_list) is 1
        assert stock.pk is stock2.pk

        # Update one
        stock3 = self.c.get_create_or_update('Stock', {'combination_id': comb}, {'icg_stock': 10})
        stock_list = models.Stock.objects.all()
        stock_list = models.Stock.objects.all()
        stock4 =  models.Stock.objects.get(pk=stock.pk)
        assert len(stock_list) is 1
        assert stock.pk is stock3.pk
        assert stock4.fields_updated == "{'icg_stock': 10}"
        assert stock4.icg_stock == 10

        # Creates other
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=8000)
        stock5 = self.c.get_create_or_update('Stock', {'combination_id': comb}, {'icg_stock': 15})
        stock_list = models.Stock.objects.all()
        assert len(stock_list) is 2
        assert stock5.pk is not stock.pk


    def test_get_create_or_update_PriceOk(self):
        # Create one
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)
        price = self.c.get_create_or_update('Price', {'combination_id': comb},
            {'iva': 15, 'pvp_siva': 15.24})
        price_list = models.Price.objects.all()
        assert len(price_list) is 1
        assert price.iva == 15

        # Get one
        price2 = self.c.get_create_or_update('Price', {'combination_id': comb}, {})
        price_list = models.Price.objects.all()
        assert len(price_list) is 1
        assert price.pk is price2.pk

        # Update one
        price3 = self.c.get_create_or_update('Price', {'combination_id': comb},
            {'iva': 10, 'pvp_siva': 14.40 })
        price_list = models.Price.objects.all()
        price_list = models.Price.objects.all()
        price4 =  models.Price.objects.get(pk=price.pk)
        assert len(price_list) is 1
        assert price.pk is price3.pk
        assert price4.fields_updated == "{'iva': 10, 'pvp_siva': 14.4}"
        assert price4.iva == 10

        # Creates other
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=8000)
        price5 = self.c.get_create_or_update('Price', {'combination_id': comb},
            {'iva': 15, 'pvp_siva': 15.24})
        price_list = models.Price.objects.all()
        assert len(price_list) is 2
        assert price5.pk is not price.pk

    def test_updateDataFromICG(self):
        prod = ProductFactory(icg_reference='', icg_id=8000)
        wasUpdate, updated_data = self.c.updateDataFromICG()
        prod2 = self.c.get_create_or_update('Product', {'icg_id': 8000}, {})
        assert prod.pk is prod2.pk
        assert prod.icg_reference is ''
        assert wasUpdate

class TestMSSQL:
    @classmethod
    def setup_class(self):
        self.ms = mssql.MSSQL()

    def test_newProduct(self):
        np  = self.ms.newProducts('')
        data = {0: [930061,7500,7500,7500,7501,7501,7502,7503,7503,7504],
            1: ['7498','0930095','0930095','0930095','0930161','0930161','0930046',
                '0930136','0930136','0930243'],
            2: ['***','12','24','8','250ML','75ML','***','S.150ML','S.400ML','11 PIEZAS'],
            3: ['***','CAR 12 ML','CAR 12 ML','CAR 12 ML','***','***','***','***','***','MADERA'],
            4: ['8712079332730','8712079312930','8712079312947','8712079312923','8712079316013',
                '8712079315993','8712079344436','8712079000677','8712079000691','8712079343378'],
            5: [' ','8712079312800','8712079312817','8712079312794',' ','8712079315979',
                '8712079260279','8712079092610','8712079092641',' '],
            6: ['Caballete Taller Haya Vesta Kit ArtCreat','Caja Tempera ArtCreation',
                'Caja Tempera ArtCreation','Caja Tempera ArtCreation','Medio Pintar Cobra',
                'Medio Pintar Cobra','Caballete Caja Trípode Haya Aurore ArtCr',
                'Fijador Concentrado Talens','Fijador Concentrado Talens','Set Medias Lunas Talens'],
            7: [1,1,1,1,1,1,1,1,1,1],
            8: [21,21,21,21,21,21,21,21,21,21],
            9: [93,93,93,93,93,93,93,93,93,93],
            10: ['TALENS ESPAÑA S.A.U.','TALENS ESPAÑA S.A.U.','TALENS ESPAÑA S.A.U.',
                'TALENS ESPAÑA S.A.U.','TALENS ESPAÑA S.A.U.','TALENS ESPAÑA S.A.U.',
                'TALENS ESPAÑA S.A.U.','TALENS ESPAÑA S.A.U.','TALENS ESPAÑA S.A.U.',
                'TALENS ESPAÑA S.A.U.'],
            11: ['2020-01-20 16:55:35','2020-01-29 13:36:12','2020-01-29 13:36:12',
                '2020-01-29 13:36:12','2019-10-16 10:03:08','2019-10-16 10:03:08',
                '2020-03-10 18:03:48','2020-01-14 17:12:39','2020-01-14 17:12:39',
                '2020-02-24 15:29:51'],
            12: ['T','T','T','T','T','T','T','T','T','T'],
            13: [14000,14000,14000,14000,30000,30000,14000,90000,90000,99990],
            14: ['ARTECREATION','ARTECREATION','ARTECREATION','ARTECREATION','COBRA',
                'COBRA','ARTECREATION','TALENS','TALENS','***'],
            15: ['F','F','F','F','F','F','F','F','F','F']}
        test_np = pd.DataFrame(data)
        #with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            #print(np)
            #print(test_np)
        assert_frame_equal(np, test_np)

    def test_newProduct_withData(self):
        str_data = ('0930061;7498;***;***;8712079332730;" ";"Caballete Taller Haya Vesta Kit ArtCreat";'
            '1;21;93;"TALENS ESPAÑA S.A.U.";"2020-01-20 16:55:35";T;14000;ARTECREATION;F\n7500;093'
            '0095;12;"CAR 12 ML";8712079312930;8712079312800;"Caja Tempera ArtCreation";1;21;93;"T'
            'ALENS ESPAÑA S.A.U.";"2020-01-29 13:36:12";T;14000;ARTECREATION;F\n7500;0930095;24;"C'
            'AR 12 ML";8712079312947;8712079312817;"Caja Tempera ArtCreation";1;21;93;"TALENS ESPA'
            'ÑA S.A.U.";"2020-01-29 13:36:12";T;14000;ARTECREATION;F\n7500;0930095;8;"CAR 12 ML";8'
            '712079312923;8712079312794;"Caja Tempera ArtCreation";1;21;93;"TALENS ESPAÑA S.A.U.";'
            '"2020-01-29 13:36:12";T;14000;ARTECREATION;F\n7501;0930161;250ML;***;8712079316013;" '
            '";"Medio Pintar Cobra";1;21;93;"TALENS ESPAÑA S.A.U.";"2019-10-16 10:03:08";T;30000;C'
            'OBRA;F\n7501;0930161;75ML;***;8712079315993;8712079315979;"Medio Pintar Cobra";1;21;9'
            '3;"TALENS ESPAÑA S.A.U.";"2019-10-16 10:03:08";T;30000;COBRA;F\n7502;0930046;***;***;'
            '8712079344436;8712079260279;"Caballete Caja Trípode Haya Aurore ArtCr";1;21;93;"TALEN'
            'S ESPAÑA S.A.U.";"2020-03-10 18:03:48";T;14000;ARTECREATION;F\n7503;0930136;S.150ML;*'
            '**;8712079000677;8712079092610;"Fijador Concentrado Talens";1;21;93;"TALENS ESPAÑA S.'
            'A.U.";"2020-01-14 17:12:39";T;90000;TALENS;F\n7503;0930136;S.400ML;***;8712079000691;'
            '8712079092641;"Fijador Concentrado Talens";1;21;93;"TALENS ESPAÑA S.A.U.";"2020-01-14'
            ' 17:12:39";T;90000;TALENS;F\n7504;0930243;"11 PIEZAS";MADERA;8712079343378;" ";"Set M'
            'edias Lunas Talens";1;21;93;"TALENS ESPAÑA S.A.U.";"2020-02-24 15:29:51";T;99990;***;F\n')
        np  = self.ms.newProducts('', str_data)
        data = {0: [930061,7500,7500,7500,7501,7501,7502,7503,7503,7504],
            1: ['7498','0930095','0930095','0930095','0930161','0930161','0930046',
                '0930136','0930136','0930243'],
            2: ['***','12','24','8','250ML','75ML','***','S.150ML','S.400ML','11 PIEZAS'],
            3: ['***','CAR 12 ML','CAR 12 ML','CAR 12 ML','***','***','***','***','***','MADERA'],
            4: ['8712079332730','8712079312930','8712079312947','8712079312923','8712079316013',
                '8712079315993','8712079344436','8712079000677','8712079000691','8712079343378'],
            5: [' ','8712079312800','8712079312817','8712079312794',' ','8712079315979',
                '8712079260279','8712079092610','8712079092641',' '],
            6: ['Caballete Taller Haya Vesta Kit ArtCreat','Caja Tempera ArtCreation',
                'Caja Tempera ArtCreation','Caja Tempera ArtCreation','Medio Pintar Cobra',
                'Medio Pintar Cobra','Caballete Caja Trípode Haya Aurore ArtCr',
                'Fijador Concentrado Talens','Fijador Concentrado Talens','Set Medias Lunas Talens'],
            7: [1,1,1,1,1,1,1,1,1,1],
            8: [21,21,21,21,21,21,21,21,21,21],
            9: [93,93,93,93,93,93,93,93,93,93],
            10: ['TALENS ESPAÑA S.A.U.','TALENS ESPAÑA S.A.U.','TALENS ESPAÑA S.A.U.',
                'TALENS ESPAÑA S.A.U.','TALENS ESPAÑA S.A.U.','TALENS ESPAÑA S.A.U.',
                'TALENS ESPAÑA S.A.U.','TALENS ESPAÑA S.A.U.','TALENS ESPAÑA S.A.U.',
                'TALENS ESPAÑA S.A.U.'],
            11: ['2020-01-20 16:55:35','2020-01-29 13:36:12','2020-01-29 13:36:12',
                '2020-01-29 13:36:12','2019-10-16 10:03:08','2019-10-16 10:03:08',
                '2020-03-10 18:03:48','2020-01-14 17:12:39','2020-01-14 17:12:39',
                '2020-02-24 15:29:51'],
            12: ['T','T','T','T','T','T','T','T','T','T'],
            13: [14000,14000,14000,14000,30000,30000,14000,90000,90000,99990],
            14: ['ARTECREATION','ARTECREATION','ARTECREATION','ARTECREATION','COBRA',
                'COBRA','ARTECREATION','TALENS','TALENS','***'],
            15: ['F','F','F','F','F','F','F','F','F','F']}
        test_np = pd.DataFrame(data)
        #with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            #print(np)
            #print(test_np)
        assert_frame_equal(np, test_np)

    def test_newPrices(self):
        np  = self.ms.newPrices('')
        data = {0: [1,1,1,1,1,1,1,1,1,1,1],
            1: [7498,7499,7500,7500,7500,7501,7501,7502,7503,7503,7503],
            2: ['***','***','12','24','8','250ML','75ML','***','S.150ML','S.400ML','S.600ML'],
            3: ['***','***','CAR 12 ML','CAR 12 ML','CAR 12 ML','***','***','***','***','***','***'],
            4: [135.45,300.00,9.00,16.00,7.00,19.00,7.00,167.90,9.00,14.00,14.00],
            5: [30, 30, 20, 20, 20, 20, 20, 30, 25, 25,0],
            6: [94.815,210.000,7.200,12.800,5.600,15.200,5.600,117.530,6.750,10.500,10.500],
            7: [40.635,90.000,1.800,3.200,1.400,3.800,1.400,50.370,2.250,3.500,3.500],
            8: [21,21,21,21,21,21,21,21,21,21,21],
            9: [111.94,247.93,7.44,13.22,5.79,15.70,5.79,138.76,7.44,11.57,11.57],
            10: [78.36,173.55,5.95,10.58,4.63,12.56,4.63,97.13,5.58,8.68,8.68],
            11: [33.58,74.38,1.49,2.64,1.16,3.14,1.16,41.63,1.86,2.89,2.89],
            12: ['2020-01-20 16:55:35','2018-01-24 11:42:23','2018-11-22 17:49:39',
                '2018-11-22 17:49:39','2018-11-22 17:49:39','2020-01-27 17:47:37',
                '2020-01-27 17:47:37','2020-01-20 16:54:51','2018-11-22 17:49:39',
                '2018-11-22 17:49:39','2018-11-22 17:49:39']}

        test_np = pd.DataFrame(data)
        #with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #    print(np)
        #    print(test_np)
        assert_frame_equal(np, test_np)

    def test_newPrices_withData(self):
        str_data = ('1;7498;***;***;135.45;30;94.815;40.635;21;111.94;78.36;33.58;"2020-01-20 16:55:35"'
            '\n1;7499;***;***;300;30;210;90;21;247.93;173.55;74.38;"2018-01-24 11:42:23"\n1;7500;'
            '12;"CAR 12 ML";9;20;7.2;1.8;21;7.44;5.95;1.49;"2018-11-22 17:49:39"\n1;7500;24;"CAR '
            '12 ML";16;20;12.8;3.2;21;13.22;10.58;2.64;"2018-11-22 17:49:39"\n1;7500;8;"CAR 12 ML"'
            ';7;20;5.6;1.4;21;5.79;4.63;1.16;"2018-11-22 17:49:39"\n1;7501;250ML;***;19;20;15.2;3.'
            '8;21;15.7;12.56;3.14;"2020-01-27 17:47:37"\n1;7501;75ML;***;7;20;5.6;1.4;21;5.79;4.63'
            ';1.16;"2020-01-27 17:47:37"\n1;7502;***;***;167.9;30;117.53;50.37;21;138.76;97.13;41.'
            '63;"2020-01-20 16:54:51"\n1;7503;S.150ML;***;9;25;6.75;2.25;21;7.44;5.58;1.86;"2018-1'
            '1-22 17:49:39"\n1;7503;S.400ML;***;14;25;10.5;3.5;21;11.57;8.68;2.89;"2018-11-22 17:4'
            '9:39"\n1;7503;S.600ML;***;14;0;10.5;3.5;21;11.57;8.68;2.89;"2018-11-22 17:49:39"')
        np  = self.ms.newPrices('', str_data)
        data = {0: [1,1,1,1,1,1,1,1,1,1,1],
            1: [7498,7499,7500,7500,7500,7501,7501,7502,7503,7503,7503],
            2: ['***','***','12','24','8','250ML','75ML','***','S.150ML','S.400ML','S.600ML'],
            3: ['***','***','CAR 12 ML','CAR 12 ML','CAR 12 ML','***','***','***','***','***','***'],
            4: [135.45,300.00,9.00,16.00,7.00,19.00,7.00,167.90,9.00,14.00,14.00],
            5: [30, 30, 20, 20, 20, 20, 20, 30, 25, 25,0],
            6: [94.815,210.000,7.200,12.800,5.600,15.200,5.600,117.530,6.750,10.500,10.500],
            7: [40.635,90.000,1.800,3.200,1.400,3.800,1.400,50.370,2.250,3.500,3.500],
            8: [21,21,21,21,21,21,21,21,21,21,21],
            9: [111.94,247.93,7.44,13.22,5.79,15.70,5.79,138.76,7.44,11.57,11.57],
            10: [78.36,173.55,5.95,10.58,4.63,12.56,4.63,97.13,5.58,8.68,8.68],
            11: [33.58,74.38,1.49,2.64,1.16,3.14,1.16,41.63,1.86,2.89,2.89],
            12: ['2020-01-20 16:55:35','2018-01-24 11:42:23','2018-11-22 17:49:39',
                '2018-11-22 17:49:39','2018-11-22 17:49:39','2020-01-27 17:47:37',
                '2020-01-27 17:47:37','2020-01-20 16:54:51','2018-11-22 17:49:39',
                '2018-11-22 17:49:39','2018-11-22 17:49:39']}

        test_np = pd.DataFrame(data)
        #with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #    print(np)
        #    print(test_np)
        assert_frame_equal(np, test_np)

    def test_newStocks(self):
        np  = self.ms.newStocks('')
        data = {0: [7498,7500,7500,7501,7502,7503,7504, 7504, 7506, 7509],
            1: ['***','12','24','75ML','***','S.400ML', '11 PIEZAS', '5 PIEZAS', '***','***'],
            2: ['***','CAR 12 ML','CAR 12 ML','***','***','***','MADERA','MADERA','***','***'],
            3: [1,1,1,1,1,1,1,1,1,1], 
            4: ["Pintor Fortuny","Pintor Fortuny","Pintor Fortuny","Pintor Fortuny","Pintor Fortuny",
                "Pintor Fortuny","Pintor Fortuny","Pintor Fortuny","Pintor Fortuny","Pintor Fortuny"],
            5: [5,4,6,2,2,66,42,12,12,190],
            6: [0,0,0,0,0,0,0,0,0,0],
            7: [5,4,6,2,2,66,42,12,12,190],
            8: ['2020-03-06 19:24:47','2020-04-22 18:40:13','2020-03-14 13:37:17',
                '2020-03-11 18:35:55','2020-03-10 18:03:48','2020-04-29 10:33:49',
                '2020-03-14 13:04:02','2020-04-25 13:16:10','2019-10-14 19:01:12','2020-04-25 13:16:10']}

        test_np = pd.DataFrame(data)
        #with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #    print(np)
        #    print(test_np)
        assert_frame_equal(np, test_np)

    def test_newStocks_withData(self):
        str_data = ('7498;***;***;01;"Pintor Fortuny";5;0;5;"2020-03-06 19:24:47"\n7500;12;"CAR 12 ML"'
            ';01;"Pintor Fortuny";4;0;4;"2020-04-22 18:40:13"\n7500;24;"CAR 12 ML";01;"Pintor Fort'
            'uny";6;0;6;"2020-03-14 13:37:17"\n7501;75ML;***;01;"Pintor Fortuny";2;0;2;"2020-03-11'
            ' 18:35:55"\n7502;***;***;01;"Pintor Fortuny";2;0;2;"2020-03-10 18:03:48"\n7503;S.400M'
            'L;***;01;"Pintor Fortuny";66;0;66;"2020-04-29 10:33:49"\n7504;"11 PIEZAS";MADERA;01;"'
            'Pintor Fortuny";42;0;42;"2020-03-14 13:04:02"\n7504;"5 PIEZAS";MADERA;01;"Pintor Fort'
            'uny";12;0;12;"2020-04-25 13:16:10"\n7506;***;***;01;"Pintor Fortuny";12;0;12;"2019-10'
            '-14 19:01:12"\n7509;***;***;01;"Pintor Fortuny";190;0;190;"2020-04-25 13:16:10"')
        np  = self.ms.newStocks('',str_data)
        data = {0: [7498,7500,7500,7501,7502,7503,7504, 7504, 7506, 7509],
            1: ['***','12','24','75ML','***','S.400ML', '11 PIEZAS', '5 PIEZAS', '***','***'],
            2: ['***','CAR 12 ML','CAR 12 ML','***','***','***','MADERA','MADERA','***','***'],
            3: [1,1,1,1,1,1,1,1,1,1], 
            4: ["Pintor Fortuny","Pintor Fortuny","Pintor Fortuny","Pintor Fortuny","Pintor Fortuny",
                "Pintor Fortuny","Pintor Fortuny","Pintor Fortuny","Pintor Fortuny","Pintor Fortuny"],
            5: [5,4,6,2,2,66,42,12,12,190],
            6: [0,0,0,0,0,0,0,0,0,0],
            7: [5,4,6,2,2,66,42,12,12,190],
            8: ['2020-03-06 19:24:47','2020-04-22 18:40:13','2020-03-14 13:37:17',
                '2020-03-11 18:35:55','2020-03-10 18:03:48','2020-04-29 10:33:49',
                '2020-03-14 13:04:02','2020-04-25 13:16:10','2019-10-14 19:01:12','2020-04-25 13:16:10']}

        test_np = pd.DataFrame(data)
        #with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #    print(np)
        #    print(test_np)
        assert_frame_equal(np, test_np)

    @pytest.mark.skipif('CODECOV_TOKEN' in os.environ, reason="Can't test from CI")
    def test_getProductData(self):
        result = self.ms.getProductData(constants.URLBASE,'0930061')
        data = {0: [7498], 1: ['0930061'], 2: ['***'], 3: ['***'], 4: ['8712079332730'],
            5: [' '], 6: ['Caballete Taller Haya Vesta Kit ArtCreat'], 7: [1], 8: [21],
            9: [93], 10: ['TALENS ESPAÑA S.A.U.'], 11: ['2020-01-20 16:55:35'],
            12: ['T'], 13: [14000], 14: ['ARTECREATION'], 15: ['F']}
        test_np = pd.DataFrame(data)
        assert_frame_equal(result, test_np)

    @pytest.mark.skipif('CODECOV_TOKEN' in os.environ, reason="Can't test from CI")
    def test_getCombinationData(self):
        result = self.ms.getCombinationData(constants.URLBASE,'0930061','***','***')
        data = {0: [7498], 1: ['0930061'], 2: ['***'], 3: ['***'], 4: ['8712079332730'],
            5: [' '], 6: ['Caballete Taller Haya Vesta Kit ArtCreat'], 7: [1], 8: [21],
            9: [93], 10: ['TALENS ESPAÑA S.A.U.'], 11: ['2020-01-20 16:55:35'],
            12: ['T'], 13: [14000], 14: ['ARTECREATION'], 15: ['F']}
        test_np = pd.DataFrame(data)
        assert_frame_equal(result, test_np)

    @pytest.mark.skipif('CODECOV_TOKEN' in os.environ, reason="Can't test from CI")
    def test_getPriceData(self):
        result = self.ms.getPriceData(constants.URLBASE,7498,'***','***')
        data = {0: [1], 1: [7498], 2: ['***'], 3: ['***'], 4: [135.45], 5: [30],
            6: [94.815], 7: [40.635], 8: [21], 9: [111.94], 10: [78.36],
            11: [33.58], 12: ['2020-01-20 16:55:35']}
        test_np = pd.DataFrame(data)
        assert_frame_equal(result, test_np)

    @pytest.mark.skipif('CODECOV_TOKEN' in os.environ, reason="Can't test from CI")
    def test_getStockData(self):
        result = self.ms.getStockData(constants.URLBASE,7498,'***','***')
        data = {0: [7498], 1: ['***'], 2: ['***'], 3: [1], 4: ["Pintor Fortuny"], 5: [5],
            6: [0], 7: [5], 8: ['2020-03-06 19:24:47']}
        test_np = pd.DataFrame(data)
        assert_frame_equal(result, test_np)

    #TODO: One test fail (no results)

@pytest.mark.django_db
class TestCommandCreateFromPrestashop:
    @classmethod
    def setup_class(self):
        self.c = controller.ControllerICGProducts()



# vim: et ts=4 sw=4
