from django.db import models
from django.utils import timezone

class Manufacturer(models.Model):
    """
    docstring here
        :param models.Model:
    """
    icg_id = models.IntegerField()
    icg_name = models.CharField(max_length=100)
    ps_id = models.IntegerField(blank=True, null=True, default=0)
    ps_name = models.CharField(max_length=100, blank=True, default="")

class Product(models.Model):
    icg_id = models.IntegerField()
    icg_reference = models.CharField(max_length=20)
    icg_name = models.CharField(max_length=100)
    ps_id = models.IntegerField(blank=True, null=True, default=0)
    ps_name = models.CharField(max_length=100, default='')
    manufacturer = models.ForeignKey('Manufacturer', on_delete=models.DO_NOTHING)
    ean13 = models.CharField(max_length=15, blank=True)
    short_description = models.TextField(blank=True)
    long_description = models.TextField(blank=True)
    created_date = models.DateTimeField(
        default=timezone.now)
    modified_date = models.DateTimeField(
        blank=True, null=True)
    updated = models.BooleanField(default=True)

    def __str__(self):
        return self.icg_name

    def speak(self):
        return self.icg_name + ' says "roar"'

class Combination(models.Model):
    name = models.CharField(max_length=100)
    icg_talla = models.CharField(max_length=15)
    icg_color = models.CharField(max_length=15)
    ps_product_attribute = models.IntegerField()
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    ean13 = models.CharField(max_length=15)
    created_date = models.DateTimeField(
            default=timezone.now)
    modified_date = models.DateTimeField(
            blank=True, null=True)
    updated = models.BooleanField()

class Stock(models.Model):
    combination_id = models.ForeignKey('Combination', on_delete=models.CASCADE)
    stock_icg = models.IntegerField()
    stock_ps = models.IntegerField()
    created_date = models.DateTimeField(
            default=timezone.now)
    modified_date = models.DateTimeField(
            blank=True, null=True)
    updated = models.BooleanField()

class Price(models.Model):
    combination_id = models.ForeignKey('Combination', on_delete=models.CASCADE)
    pvp = models.FloatField()
    dto_percent = models.FloatField()
    preu_oferta = models.FloatField()
    dto_euros = models.FloatField()
    iva = models.IntegerField()
    pvp_siva = models.FloatField()
    preu_oferta_siva = models.FloatField()
    dto_euros_siva = models.FloatField()
    created_date = models.DateTimeField(
            default=timezone.now)
    modified_date = models.DateTimeField(
            blank=True, null=True)
    updated = models.BooleanField()

