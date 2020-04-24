import factory
from . import models

class ManufacturerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.Manufacturer'
        django_get_or_create = ('icg_name','ps_name')

    icg_id = factory.Sequence(lambda n: "%03d" % n)
    icg_name = 'REMBRANDT'
    ps_name = 'Rembrandt'

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'simpleapp.Product'
        #database = 'global'
        django_get_or_create = ('icg_name','ps_name')

    icg_reference = factory.Sequence(lambda n: "%03d" % n)
    ps_name = 'Aquarela Rembrandt'
    manufacturer = factory.SubFactory(ManufacturerFactory)
    icg_name = 'Aquarela Rembrandt'

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
        ProductFactory(icg_id=1)
        man_list = models.Product.objects.all()
        assert len(man_list) is 1
