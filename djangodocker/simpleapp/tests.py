# -*- coding: utf-8 -*-
import factory
import pytest
from . import models, mssql, controller
import random
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned

class ManufacturerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.Manufacturer'
        django_get_or_create = ('icg_name','ps_name')

    icg_id = factory.Sequence(lambda n: "%03d" % n)
    icg_name = factory.Sequence(lambda n: 'Company ICG name %d' % n)
    ps_name = factory.Sequence(lambda n: 'Company PS name %d' % n)

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.Product'
        django_get_or_create = ('icg_name','ps_name', 'icg_id')

    icg_id = factory.Sequence(lambda n: "%03d" % n)
    icg_reference = factory.Sequence(lambda n: "%06d" % n)
    ps_name = factory.Sequence(lambda n: 'Product PS name %d' % n)
    manufacturer = factory.SubFactory(ManufacturerFactory)
    icg_name = factory.Sequence(lambda n: 'Product ICG name %d' % n)

class CombinationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.Combination'
        django_get_or_create = ('icg_talla','icg_color', 'product_id')

    icg_talla = factory.Sequence(lambda n: "%06d" % n)
    icg_color = factory.Sequence(lambda n: "%06d" % n)
    product_id = factory.SubFactory(ProductFactory)
    ean13 = random.randint(1000000000000,9999999999999)
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
class TestPrestashop:

    @classmethod
    def setup_class(self):
        import prestapyt
        self._api =  prestapyt.PrestaShopWebServiceDict(
            'http://prestashop/api', 'GENERATE_COMPLEX_KEY_LIKE_THIS!!', debug=True, verbose=True)


    def test_createOneManufacturer_ok(self):
        man = ManufacturerFactory()

        response = self._api.add('manufacturers', man.prestashop_object())

        assert isinstance(int(response['prestashop']['manufacturer']['id']), int)
        assert response['prestashop']['manufacturer']['active'] is "1"


    def test_createOneProduct_ok(self):
        prod = ProductFactory()

        response = self._api.add('products', prod.prestashop_object())

        assert isinstance(int(response['prestashop']['product']['id']), int)
        assert response['prestashop']['product']['active'] is "1"


    def test_createOneCombination_ok(self):
        comb = CombinationFactory()

        response = self._api.add('combinations', comb.prestashop_object())

        assert isinstance(int(response['prestashop']['combination']['id']), int)


    def test_updateOnePrice_ok(self):
        comb = CombinationFactory()
        response = self._api.add('combinations', comb.prestashop_object())
        comb.ps_id = response['prestashop']['combination']['id']
        assert comb.ps_id
        price = PriceFactory(combination_id = comb)

        response = self._api.edit('combinations', price.update_price())

        assert isinstance(int(response['prestashop']['combination']['id']), int)


@pytest.mark.django_db
class TestController:
    def test_saveNewProduts(self):
        c = controller.Controller()

        c.saveNewProducts()

        prod_list = models.Product.objects.all()
        man_list = models.Manufacturer.objects.all()
        comb_list = models.Combination.objects.all()
        assert len(prod_list) is 6
        assert len(man_list) is 4
        assert len(comb_list) is 10

    def test_get_create_or_update_manufacturer_createOne(self):
        c = controller.Controller()

        man = c.get_create_or_update_manufacturer(14000, "ARTECREATION")

        man_list = models.Manufacturer.objects.all()
        assert len(man_list) is 1

    def test_get_create_or_update_manufacturer_createOneGetOne(self):
        c = controller.Controller()

        man1 = c.get_create_or_update_manufacturer(14000, "ARTECREATION")
        man2 = c.get_create_or_update_manufacturer(14000, "ARTECREATION")

        man_list = models.Manufacturer.objects.all()
        assert len(man_list) is 1
        assert man1.pk is man2.pk

    def test_get_create_or_update_manufacturer_createOneUpdateOne(self):
        c = controller.Controller()

        man1 = c.get_create_or_update_manufacturer(14000, "ARTECREATION")
        man2 = c.get_create_or_update_manufacturer(14000, "ARTCREATION")

        man_list = models.Manufacturer.objects.all()
        assert len(man_list) is 1
        assert man1.pk is man2.pk

    def test_get_create_or_update_manufacturer_createTwo(self):
        c = controller.Controller()

        man1 = c.get_create_or_update_manufacturer(14000, "ARTECREATION")
        man2 = c.get_create_or_update_manufacturer(15000, "COBRA")

        man_list = models.Manufacturer.objects.all()
        assert len(man_list) is 2
        assert man1.pk is not man2.pk

    def test_get_create_or_update_product_createOne(self):
        c = controller.Controller()
        man = ManufacturerFactory()

        prod = c.get_create_or_update_product(7500, "0930095", "Caja Témpera ArtCreation", True, man)

        prod_list = models.Product.objects.all()
        assert len(prod_list) is 1

    def test_get_create_or_update_product_createOneGetOne(self):
        c = controller.Controller()
        man = ManufacturerFactory()

        prod1 = c.get_create_or_update_product(7500, "0930095", "Caja Témpera ArtCreation", True, man)
        prod2 = c.get_create_or_update_product(7500, "0930095", "Caja Témpera ArtCreation", True, man)

        prod_list = models.Product.objects.all()
        assert len(prod_list) is 1
        assert prod1.pk is prod2.pk

    def test_get_create_or_update_product_createOneUpdateOne(self):
        c = controller.Controller()
        man = ManufacturerFactory()

        prod1 = c.get_create_or_update_product(7500, "09300956", "Caja Tempera ArtCreation", True, man)
        prod2 = c.get_create_or_update_product(7500, "0930095", "Caja Témpera ArtCreation", False, man)

        prod_list = models.Product.objects.all()
        prod = models.Product.objects.get(icg_id = 7500)
        assert len(prod_list) is 1
        assert prod1.pk is prod2.pk
        assert prod.icg_reference == "0930095"
        assert prod.icg_name == "Caja Témpera ArtCreation"

    def test_get_create_or_update_product_createTwo(self):
        c = controller.Controller()
        man = ManufacturerFactory()

        prod1 = c.get_create_or_update_product(7500, "0930095", "Caja Tempera ArtCreation", True, man)
        prod2 = c.get_create_or_update_product(7501, "0930096", "Caballete ArtCreation", False, man)

        prod_list = models.Product.objects.all()
        assert len(prod_list) is 2
        assert prod1.pk is not prod2.pk


    def test_get_create_or_update_combination_createOne(self):
        c = controller.Controller()
        prod = ProductFactory()

        comb = c.get_create_or_update_combination(prod, "12", "12 ML", False, "8712079332730")

        comb_list = models.Combination.objects.all()
        assert len(comb_list) is 1

    def test_get_create_or_update_combination_createOneGetOne(self):
        c = controller.Controller()
        prod = ProductFactory()

        comb1 = c.get_create_or_update_combination(prod, "12", "12 ML", False, "8712079332730")
        comb2 = c.get_create_or_update_combination(prod, "12", "12 ML", False, "8712079332730")

        comb_list = models.Combination.objects.all()
        assert len(comb_list) is 1
        assert comb1.pk is comb2.pk

    def test_get_create_or_update_combination_createOneUpdateOne(self):
        c = controller.Controller()
        prod = ProductFactory()

        comb1 = c.get_create_or_update_combination(prod, "12", "12 ML", False, "8712079332730")
        comb2 = c.get_create_or_update_combination(prod, "12", "12 ML", True, "8712079332731")

        comb_list = models.Combination.objects.all()
        comb = models.Combination.objects.get(icg_talla = "12 ML", icg_color="12", product_id = prod )
        assert len(comb_list) is 1
        assert comb1.pk is comb2.pk
        assert comb.ean13 == "8712079332731"
        assert comb.discontinued == True

    def test_get_create_or_update_combination_createTwo(self):
        c = controller.Controller()
        prod = ProductFactory()

        comb1 = c.get_create_or_update_combination(prod, "12", "12 ML", False, "8712079332730")
        comb2 = c.get_create_or_update_combination(prod, "12", "120 ML", True, "8712079332731")

        comb_list = models.Combination.objects.all()
        assert len(comb_list) is 2
        assert comb1.pk is not comb2.pk



@pytest.mark.django_db
class TestControllerPrices:

    def test_get_create_or_update_price_createOne(self):
        c = controller.ControllerPrices()
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)

        price = c.get_create_or_update_price(comb, "15", "21", "14.12")

        price_list = models.Price.objects.all()
        assert len(price_list) is 1
        assert eval(price.pvp_siva) == 14.12
        assert eval(price.iva) == 21
        assert eval(price.dto_percent) == 15

    def test_get_create_or_update_price_createOneGetOne(self):
        c = controller.ControllerPrices()
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)

        price1 = c.get_create_or_update_price(comb, "15", "21", "14.12")
        price2 = c.get_create_or_update_price(comb, "15", "21", "14.12")

        price = models.Price.objects.get(combination_id = comb)
        price_list = models.Price.objects.all()
        assert len(price_list) is 1
        assert price1.pk is price2.pk

    def test_get_create_or_update_price_createOneUpdateOne(self):
        c = controller.ControllerPrices()
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)

        price1 = c.get_create_or_update_price(comb, "15", "21", "14.12")
        price2 = c.get_create_or_update_price(comb, "15", "16", "13.12")

        price = models.Price.objects.get(combination_id = comb)
        price_list = models.Price.objects.all()
        assert len(price_list) is 1
        assert price1.pk is price2.pk
        assert price.pvp_siva == 13.12
        assert price.iva == 16
        assert price.dto_percent == 15

    def test_get_create_or_update_price_createTwo(self):
        c = controller.ControllerPrices()
        prod = ProductFactory()
        comb1 = CombinationFactory(icg_talla="***", icg_color="***", product_id = prod)
        comb2 = CombinationFactory(icg_talla="1", icg_color="***", product_id = prod)

        price1 = c.get_create_or_update_price(comb1, "15", "21", "14.12")
        price2 = c.get_create_or_update_price(comb2, "15", "16", "13.12")

        price_list = models.Price.objects.all()
        prod_list = models.Product.objects.all()
        assert len(prod_list) is 1
        assert len(price_list) is 2
        assert price1.pk is not price2.pk

    def test_saveNewPrices(self):
        c = controller.ControllerPrices()

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

        c.saveNewPrices()

        prod_list = models.Product.objects.all()
        man_list = models.Manufacturer.objects.all()
        comb_list = models.Combination.objects.all()
        assert len(prod_list) is 6
        assert len(comb_list) is 10



@pytest.mark.django_db
class TestControllerStocks:

    def test_get_create_or_update_stock_createOne(self):
        c = controller.ControllerStocks()
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)

        stock = c.get_create_or_update_stock(comb, "15")

        stock_list = models.Stock.objects.all()
        assert len(stock_list) is 1
        assert eval(stock.icg_stock) == 15

    def test_get_create_or_update_stock_createOneGetOne(self):
        c = controller.ControllerStocks()
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)

        stock1 = c.get_create_or_update_stock(comb, "15")
        stock2 = c.get_create_or_update_stock(comb, "15")

        stock = models.Stock.objects.get(combination_id = comb)
        stock_list = models.Stock.objects.all()
        assert len(stock_list) is 1
        assert stock1.pk is stock2.pk

    def test_get_create_or_update_stock_createOneUpdateOne(self):
        c = controller.ControllerStocks()
        comb = CombinationFactory(icg_talla="***", icg_color="***", product_id__icg_id=7498)

        stock1 = c.get_create_or_update_stock(comb, "15")
        stock2 = c.get_create_or_update_stock(comb, "13")

        stock = models.Stock.objects.get(combination_id = comb)
        stock_list = models.Stock.objects.all()
        assert len(stock_list) is 1
        assert stock1.pk is stock2.pk
        assert stock.icg_stock == 13

    def test_get_create_or_update_stock_createTwo(self):
        c = controller.ControllerStocks()
        prod = ProductFactory()
        comb1 = CombinationFactory(icg_talla="***", icg_color="***", product_id = prod)
        comb2 = CombinationFactory(icg_talla="1", icg_color="***", product_id = prod)

        stock1 = c.get_create_or_update_stock(comb1, "15")
        stock2 = c.get_create_or_update_stock(comb2, "112")

        stock_list = models.Stock.objects.all()
        prod_list = models.Product.objects.all()
        assert len(prod_list) is 1
        assert len(stock_list) is 2
        assert stock1.pk is not stock2.pk

    def test_saveNewStocks(self):
        c = controller.ControllerStocks()

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

        c.saveNewStocks()

        prod_list = models.Product.objects.all()
        comb_list = models.Combination.objects.all()
        assert len(prod_list) is 8
        assert len(comb_list) is 10

# vim: et ts=4 sw=4
