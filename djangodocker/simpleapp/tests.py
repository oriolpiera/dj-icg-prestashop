# -*- coding: utf-8 -*-
import factory
import pytest
from . import models, mssql, controller, prestashop
import random
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
import prestapyt

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
        django_get_or_create = ('pvp','dto_percent', 'combination_id')

    pvp = 0
    dto_percent = 0
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
        django_get_or_create = ('ps_icg_type', 'ps_id')

    ps_id = 0
    ps_icg_type = 'talla'
    product_id = factory.SubFactory(ProductFactory)

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


@pytest.mark.django_db
class TestControllerPrestashop:

    @classmethod
    def setup_class(self):

        self._api =  prestapyt.PrestaShopWebServiceDict(
            'http://prestashop/api', 'GENERATE_COMPLEX_KEY_LIKE_THIS!!', debug=True, verbose=True)
        self.p = prestashop.ControllerPrestashop()


    def test_createOneManufacturer_ok(self):
        man = ManufacturerFactory()

        man_ps = self.p.get_or_create_manufacturer(man)

        assert man.ps_id
        assert man_ps['manufacturer']['id']

    def test_createOneManufacturerGetOne_ok(self):
        man = ManufacturerFactory()

        man_ps1 = self.p.get_or_create_manufacturer(man)
        man_ps2 = self.p.get_or_create_manufacturer(man)

        assert man.ps_id
        assert man_ps1['manufacturer'] == man_ps2['manufacturer']

    def test_createOneManufacturerGetOneUpdateOne_ok(self):
        man = ManufacturerFactory()

        man_ps1 = self.p.get_or_create_manufacturer(man)
        man.icg_name = 'other_name'
        man_ps2 = self.p.get_or_create_manufacturer(man)

        assert man_ps1['manufacturer'] != man_ps2['manufacturer']
        assert man_ps2['manufacturer']['name'] == 'other_name'


    def test_createTwoManufacturers_ok(self):
        man1 = ManufacturerFactory()
        man2 = ManufacturerFactory()

        man_ps1 = self.p.get_or_create_manufacturer(man1)
        man_ps2 = self.p.get_or_create_manufacturer(man2)

        assert man1.ps_id
        assert man2.ps_id
        assert man_ps1['manufacturer'] is not man_ps2['manufacturer']


    def test_createOneProduct_ok(self):
        prod = ProductFactory()

        prod_ps = self.p.get_or_create_product(prod)

        assert prod.ps_id
        assert prod_ps['product']['id']

    def test_createOneProduct_noCreate(self):
        prod = ProductFactory(visible_web=False)

        prod_ps = self.p.get_or_create_product(prod)

        assert not prod.ps_id
        assert prod_ps == {}

    def test_createOneProductGetOne_ok(self):
        prod = ProductFactory()

        prod_ps1 = self.p.get_or_create_product(prod)
        prod_ps2 = self.p.get_or_create_product(prod)

        assert prod.ps_id
        assert prod_ps1['product'] == prod_ps2['product']

    def test_createTwoProducts_ok(self):
        prod1 = ProductFactory()
        prod2 = ProductFactory()

        prod_ps1 = self.p.get_or_create_product(prod1)
        prod_ps2 = self.p.get_or_create_product(prod2)

        assert prod1.ps_id
        assert prod2.ps_id
        assert prod_ps1['product'] != prod_ps2['product']


    def test_get_or_create_combination_ok(self):
        # Create one
        comb = CombinationFactory(icg_talla="12", icg_color="***", product_id__icg_id=7498)
        assert not comb.discontinued
        comb_ps1 = self.p.get_or_create_combination(comb)
        assert comb.ps_id
        assert comb_ps1['combination']['id']
        po_list = models.ProductOption.objects.all()
        pov_list = models.ProductOptionValue.objects.all()
        assert len(po_list) is 2
        assert len(pov_list) is 2

        # Get one
        comb_ps2 = self.p.get_or_create_combination(comb)
        assert comb_ps1['combination']['id'] == comb_ps2['combination']['id']

        # Create other
        comb2 = CombinationFactory(icg_talla="24", icg_color="***", product_id__icg_id=7499)
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
        with pytest.raises(prestapyt.prestapyt.PrestaShopWebServiceError):
            self.p.get_or_create_combination(comb)


    def test_get_or_create_product_options_ok(self):
        # Create one
        po = ProductOptionFactory()
        po_ps1 = self.p.get_or_create_product_options(po)
        assert po.ps_id
        assert po_ps1['product_option']['id']

        # Get one
        po_ps2 = self.p.get_or_create_product_options(po)
        assert po_ps1['product_option']['id'] == po_ps2['product_option']['id']

        # Create other
        po2 = ProductOptionFactory()
        po_ps3 = self.p.get_or_create_product_options(po2)
        assert po_ps3['product_option']['id'] != po_ps2['product_option']['id']


    def test_get_or_create_product_option_value_ok(self):
        # Create one
        pov = ProductOptionValueFactory()
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

    def test_get_or_create_specific_price_ok(self):
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
        comb2 = CombinationFactory()
        sp2 = SpecificPriceFactory(combination_id = comb2)
        comb_ps3 = self.p.get_or_create_combination(comb2)
        sp_ps3 = self.p.get_or_create_specific_price(sp2)
        assert sp_ps1['specific_price']['id'] != sp_ps3['specific_price']['id']


    def test_carregaNous_ok(self):
        #import pudb;pu.db
        comb = CombinationFactory.create_batch(2)
        assert len(models.Product.objects.all()) is 2
        assert len(models.ProductOption.objects.all()) is 0

        created = self.p.carregaNous()
        created2 = self.p.carregaNous()

        assert len(models.Manufacturer.objects.filter(updated = True)) is 0
        assert len(models.Manufacturer.objects.exclude(ps_id = 0)) is 2
        assert len(models.Product.objects.filter(updated = True)) is 0
        assert len(models.Product.objects.exclude(ps_id = 0)) is 2
        assert len(models.ProductOption.objects.filter(updated = True)) is 0
        assert len(models.ProductOption.objects.exclude(ps_id = 0)) is 8
        assert len(models.ProductOptionValue.objects.exclude(ps_id = 0)) is 4
        assert len(models.Combination.objects.exclude(ps_id = 0)) is 2

        assert len(created['ps_man']) is 2
        assert len(created['ps_prod']) is 2
        assert len(created['ps_po']) is 4
        #assert len(created['ps_pov']) is 4
        assert len(created['ps_comb']) is 2

        for n in  created['ps_man']:
            assert self._api.get('manufacturers', n)

        for n in  created['ps_prod']:
            assert self._api.get('products', n)

        for n in  created['ps_po']:
            assert self._api.get('product_options', n)

        for n in  created['ps_pov']:
            assert self._api.get('product_option_values', n)
 
        #REmove whem delete element
        #for n in created['ps_comb']:
        #    assert self._api.get('combinations', n)

        created2 = self.p.carregaNous()

        assert len(created2['ps_man']) is 0
        assert len(created2['ps_prod']) is 0
        assert len(created2['ps_po']) is 0
        assert len(created2['ps_pov']) is 4
        assert len(created2['ps_comb']) is 0

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


@pytest.mark.django_db
class TestControllerICGPrices:
    @classmethod
    def setup_class(self):
        self.c = controller.ControllerICGPrices()

    def test_get_create_or_update_price_createOne(self):
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)

        price = self.c.get_create_or_update_price(comb, "15", "21", "14.12")

        price_list = models.Price.objects.all()
        assert len(price_list) is 1
        assert eval(price.pvp_siva) == 14.12
        assert eval(price.iva) == 21
        assert eval(price.dto_percent) == 15

    def test_get_create_or_update_price_createOneGetOne(self):
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)

        price1 = self.c.get_create_or_update_price(comb, "15", "21", "14.12")
        price2 = self.c.get_create_or_update_price(comb, "15", "21", "14.12")

        price = models.Price.objects.get(combination_id = comb)
        price_list = models.Price.objects.all()
        assert len(price_list) is 1
        assert price1.pk is price2.pk

    def test_get_create_or_update_price_createOneUpdateOne(self):
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)

        price1 = self.c.get_create_or_update_price(comb, "15", "21", "14.12")
        price2 = self.c.get_create_or_update_price(comb, "15", "16", "13.12")

        price = models.Price.objects.get(combination_id = comb)
        price_list = models.Price.objects.all()
        assert len(price_list) is 1
        assert price1.pk is price2.pk
        assert price.pvp_siva == 13.12
        assert price.iva == 16
        assert price.dto_percent == 15

    def test_get_create_or_update_price_createTwo(self):
        prod = ProductFactory()
        comb1 = CombinationFactory(icg_talla="***", icg_color="***", product_id = prod)
        comb2 = CombinationFactory(icg_talla="1", icg_color="***", product_id = prod)

        price1 = self.c.get_create_or_update_price(comb1, "15", "21", "14.12")
        price2 = self.c.get_create_or_update_price(comb2, "15", "16", "13.12")

        price_list = models.Price.objects.all()
        prod_list = models.Product.objects.all()
        assert len(prod_list) is 1
        assert len(price_list) is 2
        assert price1.pk is not price2.pk

    def test_saveNewPrices(self):
        comb1 = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)
        comb1 = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7499)
        prod3 = ProductFactory(icg_id = 7500)
        comb1 = CombinationFactory(icg_talla="12", icg_color="CAR 12 ML", product_id__icg_id=7500)
        comb1 = CombinationFactory(icg_talla="24", icg_color="CAR 12 ML", product_id__icg_id=7500)
        comb1 = CombinationFactory(icg_talla="8", icg_color="CAR 12 ML", product_id__icg_id=7500)
        prod4 = ProductFactory(icg_id = 7501)
        comb1 = CombinationFactory(icg_talla="250ML", icg_color="***", product_id=prod4)
        comb1 = CombinationFactory(icg_talla="75ML", icg_color="***", product_id=prod4)
        comb1 = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7502)
        prod6 = ProductFactory(icg_id = 7503)
        comb1 = CombinationFactory(icg_talla="S.150ML", icg_color="***", product_id=prod6)
        comb1 = CombinationFactory(icg_talla="S.400ML", icg_color="***", product_id=prod6)

        self.c.saveNewPrices()

        prod_list = models.Product.objects.all()
        man_list = models.Manufacturer.objects.all()
        comb_list = models.Combination.objects.all()
        assert len(prod_list) is 6
        assert len(comb_list) is 10



@pytest.mark.django_db
class TestControllerStocks:
    @classmethod
    def setup_class(self):
        self.c = controller.ControllerICGStocks()

    def test_get_create_or_update_stock_createOne(self):
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)

        stock = self.c.get_create_or_update_stock(comb, "15")

        stock_list = models.Stock.objects.all()
        assert len(stock_list) is 1
        assert eval(stock.icg_stock) == 15

    def test_get_create_or_update_stock_createOneGetOne(self):
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)

        stock1 = self.c.get_create_or_update_stock(comb, "15")
        stock2 = self.c.get_create_or_update_stock(comb, "15")

        stock = models.Stock.objects.get(combination_id = comb)
        stock_list = models.Stock.objects.all()
        assert len(stock_list) is 1
        assert stock1.pk is stock2.pk

    def test_get_create_or_update_stock_createOneUpdateOne(self):
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)

        stock1 = self.c.get_create_or_update_stock(comb, "15")
        stock2 = self.c.get_create_or_update_stock(comb, "13")

        stock = models.Stock.objects.get(combination_id = comb)
        stock_list = models.Stock.objects.all()
        assert len(stock_list) is 1
        assert stock1.pk is stock2.pk
        assert stock.icg_stock == 13

    def test_get_create_or_update_stock_createTwo(self):
        prod = ProductFactory()
        comb1 = CombinationFactory(icg_talla="***", icg_color="***", product_id = prod)
        comb2 = CombinationFactory(icg_talla="1", icg_color="***", product_id = prod)

        stock1 = self.c.get_create_or_update_stock(comb1, "15")
        stock2 = self.c.get_create_or_update_stock(comb2, "112")

        stock_list = models.Stock.objects.all()
        prod_list = models.Product.objects.all()
        assert len(prod_list) is 1
        assert len(stock_list) is 2
        assert stock1.pk is not stock2.pk

    def test_saveNewStocks(self):
        CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)
        prod3 = ProductFactory(icg_id = 7500)
        CombinationFactory(icg_talla="12", icg_color="CAR 12 ML", product_id__icg_id=7500)
        CombinationFactory(icg_talla="24", icg_color="CAR 12 ML", product_id__icg_id=7500)
        CombinationFactory(icg_talla="75ML", icg_color="***", product_id__icg_id=7501)
        CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7502)
        CombinationFactory(icg_talla="S.400ML", icg_color="***", product_id__icg_id=7503)
        prod3 = ProductFactory(icg_id = 7504)
        CombinationFactory(icg_talla="11 PIEZAS", icg_color="MADERA", product_id__icg_id=7504)
        CombinationFactory(icg_talla="5 PIEZAS", icg_color="MADERA", product_id__icg_id=7504)
        CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7506)
        CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7509)

        self.c.saveNewStocks()

        prod_list = models.Product.objects.all()
        comb_list = models.Combination.objects.all()
        assert len(prod_list) is 8
        assert len(comb_list) is 10

# vim: et ts=4 sw=4
