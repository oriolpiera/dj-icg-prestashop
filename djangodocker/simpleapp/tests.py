import factory
from . import models

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
        django_get_or_create = ('icg_name','ps_name')

    icg_id = factory.Sequence(lambda n: "%03d" % n)
    icg_reference = factory.Sequence(lambda n: "%06d" % n)
    ps_name = factory.Sequence(lambda n: 'Product PS name %d' % n)
    manufacturer = factory.SubFactory(ManufacturerFactory)
    icg_name = factory.Sequence(lambda n: 'Product ICG name %d' % n)

class CombinationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.Combination'
        django_get_or_create = ('icg_talla','icg_color')

    icg_talla = factory.Sequence(lambda n: "%06d" % n)
    icg_color = factory.Sequence(lambda n: "%06d" % n)
    product_id = factory.SubFactory(ProductFactory)

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
        django_get_or_create = ('pvp','dto_percent')

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

import pytest
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
        man_list = models.Combination.objects.all()
        assert len(man_list) is 1

    def test_createOneStock_ok(self):
        StockFactory()
        man_list = models.Stock.objects.all()
        assert len(man_list) is 1

    def test_createOnePrice_ok(self):
        PriceFactory()
        man_list = models.Price.objects.all()
        assert len(man_list) is 1


import pytest
@pytest.mark.django_db
class TestPrestashop:
    def test_createOneManufacturer_ok(self):
        man = ManufacturerFactory()
        from prestapyt import PrestaShopWebService
        prestashop = PrestaShopWebService('http://prestashop/api', 'GENERATE_COMPLEX_KEY_LIKE_THIS!!', json=True)
        p = prestashop.get('manufacturers', options={'schema': 'blank'})

        response = prestashop.add('manufacturers', man.prestashop_object())

        assert response.status_code is 201
        response_json = response.json()
        assert response_json['manufacturer']['name'].startswith("Company ")
        assert response_json['manufacturer']['active'] is "1"

# vim: et ts=4 sw=4
