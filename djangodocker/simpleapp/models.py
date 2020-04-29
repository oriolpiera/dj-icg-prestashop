# -*- coding: utf-8 -*-
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
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    updated = models.BooleanField(default=True)
    fields_updated = models.CharField(max_length=100, default="{}")

    class Meta:
        verbose_name = 'manufacturer'
        verbose_name_plural = 'manufacturers'

    def saved_in_prestashop(self):
        return ps_id

    def compareICG(self, man):
        result = {}
        if self.icg_name != man.icg_name:
            result['icg_name'] = man.icg_name
        return result

    def compare(self, man):
        result = {}
        if self.ps_name != man['manufacturer']['name']:
            result['ps_name'] = man['manufacturer']['name']
        return result

    @classmethod
    def createFromPS(cls, man_dict):
        man = cls(icg_id=0, icg_name = '',
             ps_name = man_dict['manufacturer']['name'])
        return man

    def prestashop_object(self):
        return {
            "manufacturer": {
                "active": "1",
                "name": self.ps_name or self.icg_name,
            }
        }


class Product(models.Model):
    icg_id = models.IntegerField(unique=True)
    icg_reference = models.CharField(max_length=20)
    icg_name = models.CharField(max_length=100)
    ps_id = models.IntegerField(blank=True, null=True, default=0)
    ps_name = models.CharField(max_length=100, default='')
    manufacturer = models.ForeignKey('Manufacturer', on_delete=models.DO_NOTHING)
    short_description = models.TextField(blank=True)
    long_description = models.TextField(blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(blank=True, null=True)
    icg_modified_date = models.DateTimeField(blank=True, null=True)
    updated = models.BooleanField(default=True)
    visible_web = models.BooleanField(default=True)
    fields_updated = models.CharField(max_length=200, default="{}")


    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def __str__(self):
        return "Producte %d de nom %s i referencia %s" % (self.icg_id, self.icg_name, self.icg_reference)

    def saved_in_prestashop(self):
        return ps_id

    @classmethod
    def create(cls, icg_id, icg_reference, icg_name, manufacturer):
        product = cls(icg_id=icg_id, icg_reference=icg_reference,
            icg_name=icg_name, manufacturer=manufacturer)
        return product

    def compareICG(self, product):
        result = {}
        if self.icg_name != product.icg_name:
            result['icg_name'] = product.icg_name
        if self.icg_reference != product.icg_reference:
            result['icg_reference'] = product.icg_reference
        if self.manufacturer != product.manufacturer:
            result['manufacturer'] = product.manufacturer.icg_id
        if self.visible_web != product.visible_web:
            result['visible_web'] = "0"
        return result

    def compare(self, product):
        result = {}
        if hasattr(product, 'icg_id'):
            if self.icg_reference != product.icg_reference:
                result['icg_reference'] = product.icg_reference
            if self.manufacturer != product.manufacturer:
                result['manufacturer'] = product.manufacturer.icg_id
            if self.icg_name != product.icg_name:
                result['icg_name'] = product.icg_name
            if self.visible_web != product.visible_web:
                result['visible_web'] = "0"
        elif isinstance(product, dict):
            if self.icg_reference != product['product']['reference']:
                result['icg_reference'] = product['product']['reference']
            if self.manufacturer.ps_id != product['product']['id_manufacturer']:
                result['manufacturer'] = product['product']['id_manufacturer']
            if self.icg_name != product['product']['name']['language']['value']:
                result['icg_name'] = product['product']['name']['language']['value']
            if self.visible_web != product['product']['active']:
                result['visible_web'] = product['product']['active']

        return result

    def prestashop_object(self):
        return {
            "product": {
                "id_manufacturer": self.manufacturer.ps_id,
                "id_category_default": "4",
                "reference": self.icg_reference,
                "state": "1",
                "price": "0",
                "active": "1",
                "redirect_type": "301-category",
                "available_for_order": "1",
                "show_condition": "0",
                "condition": "new",
                "show_price": "1",
                "indexed": "1",
                "visibility": "both",
                "id_supplier": "0",
                "additional_delivery_times": "0",
                "ecotax": "0.000000",
                "online_only": "0",
                "height": "0.000000",
                'name': {
                    'language': [{
                        'attrs': {
                            'id': '1',
                            'href': {'value': 'http://localhost:8080/api/languages/1',
                            'xmlns': 'http://www.w3.org/1999/xlink'},
                        },
                        'value': self.icg_name
                        }],
                },
                "link_rewrite": {
                    'language': [{
                        'attrs': {
                            'id': '1',
                            'href': {'value': 'http://localhost:8080/api/languages/1',
                            'xmlns': 'http://www.w3.org/1999/xlink'},
                        },
                        'value': "name-rewrite"
                        }],
                }
            }
        }

class Combination(models.Model):
    ps_id = models.IntegerField(blank=True, null=True) #previous ps_product_attribut
    icg_talla = models.CharField(max_length=15)
    icg_color = models.CharField(max_length=15)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    ean13 = models.CharField(max_length=15, blank=True)
    minimal_quantity = models.IntegerField(default=1)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(blank=True, null=True)
    updated = models.BooleanField(default=True)
    discontinued = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'combination'
        verbose_name_plural = 'combinations'

    def __str__(self):
        return "Combinació del Producte %s de color %s i talla %s" % (
            str(self.product_id.icg_id), self.icg_color, self.icg_talla)

    def saved_in_prestashop(self):
        return ps_id

    def prestashop_object(self):
        return {
            "combinations": {
                "id_product": self.product_id.ps_id,
                "ean13": self.ean13,
                "price": "0",
                "minimal_quantity": self.minimal_quantity,
            }
        }

    def compare(self, product):
        result = {}
        if self.ean13 != product.ean13:
            result['ean13'] = product.ean13
        if self.discontinued != product.discontinued:
            result['discontinued'] = product.discontinued
        return result

class Stock(models.Model):
    combination_id = models.OneToOneField('Combination', on_delete=models.CASCADE)
    icg_stock = models.IntegerField(default=0)
    ps_stock = models.IntegerField(default=0)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(blank=True, null=True)
    icg_modified_date = models.DateTimeField(blank=True, null=True)
    updated = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'stock'
        verbose_name_plural = 'stocks'

    def prestashop_object(self):
        return {
            "combinations": {
                "id_product": self.product_id.ps_id,
                "ean13": self.ean13,
                "price": "0",
                "minimal_quantity": self.combination_id.minimal_quantity,
            }
        }

class Price(models.Model):
    combination_id = models.OneToOneField('Combination', on_delete=models.CASCADE, primary_key=True)
    ps_id = models.IntegerField(default=0)
    pvp = models.FloatField(default=0)
    dto_percent = models.FloatField(default=0)
    preu_oferta = models.FloatField(default=0)
    dto_euros = models.FloatField(default=0)
    iva = models.IntegerField(default=0)
    pvp_siva = models.FloatField(default=0)
    preu_oferta_siva = models.FloatField(default=0)
    dto_euros_siva = models.FloatField(default=0)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(blank=True, null=True)
    icg_modified_date = models.DateTimeField(blank=True, null=True)
    updated = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'price'
        verbose_name_plural = 'prices'

    def compare(self, product):
        result = {}
        if self.dto_percent != product.dto_percent:
            result['dto_percent'] = product.dto_percent
        if self.iva != product.iva:
            result['iva'] = product.iva
        if self.pvp_siva != product.pvp_siva:
            result['pvp_siva'] = product.pvp_siva
        return result

    def update_price(self):
        return {
            "combinations": {
                "id": self.combination_id.ps_id,
                "id_product": self.combination_id.product_id.ps_id,
                "price": self.pvp_siva,
                "minimal_quantity": self.combination_id.minimal_quantity,
            }
        }

    def update_discount(self):
        return {
            "specific_prices": {
                "id": self.ps_id,
                "reduction": str(float(self.dto_percent/100)),
                "id_shop": 0,
                "id_cart": 0,
                "id_product": self.combination_id.product_id.ps_id,
                "id_product_attribute": self.combination_id.ps_id,
                "id_currency": 0,
            }
        }

    def create_discount(self):
        return {
            "specific_prices": {
                "reduction": str(float(self.dto_percent/100)),
                "id_product": self.combination_id.product_id.ps_id,
                "id_product_attribute": self.combination_id.ps_id,
                "id_shop": 0,
                "id_cart": 0,
                "id_currency": 0,
                "id_country": 0,
                "id_group": 0,
                "id_customer": 0,
                "price": 0,
                "reduction_tax": 0,
                "from": '0000-00-00 00:00:00',
                "to": '0000-00-00 00:00:00',
                "reduction_type": 'percentage',
                "from_quantity": 1,
            }
        }

class ProductOption(models.Model):
    ps_id = models.IntegerField(blank=True, null=True, default=0)
    ps_name = models.CharField(max_length=100, default='')
    ps_icg_type = models.CharField(max_length=10, default='') #talla o color
    ps_public_name = models.CharField(max_length=100, default='')
    ps_group_type = models.CharField(max_length=15, default='')
    ps_position = models.IntegerField(default=0)
    ps_iscolor = models.BooleanField(default=False)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(blank=True, null=True)
    updated = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'product_option'
        verbose_name_plural = 'products_options'

    @classmethod
    def create(cls, ps_name, product):
        ps_icg_type = ps_name.split('_')[1]
        po = cls(ps_name = ps_name, ps_icg_type = ps_icg_type, product_id = product)
        return po

    def __str__(self):
        return "Producte combinacio %d del producte amb ref %s i de nom  %s" % (self.ps_id, self.product_id.icg_reference, self.ps_name)

    def saved_in_prestashop(self):
        return ps_id

    def compareICG(self, po):
        return {}

class ProductOptionValue(models.Model):
    icg_name = models.CharField(max_length=15, default='')
    ps_id = models.IntegerField(blank=True, null=True, default=0)
    ps_name = models.CharField(max_length=100, default='')
    po_id = models.ForeignKey('ProductOption', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(blank=True, null=True)
    updated = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'product_option_value'
        verbose_name_plural = 'products_options_values'

    def __str__(self):
        return "Atribut %s del grup %s" % (self.icg_name, self.po_id.ps_name)

    def saved_in_prestashop(self):
        return ps_id

class SpecificPrice(models.Model):
    ps_id = models.IntegerField(default=0)
    ps_reduction = models.FloatField(default=0)
    combination_id = models.OneToOneField('Combination', on_delete=models.CASCADE, primary_key=True)
    dto_percent = models.FloatField(default=0)
    dto_euros = models.FloatField(default=0)
    dto_euros_siva = models.FloatField(default=0)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(blank=True, null=True)
    icg_modified_date = models.DateTimeField(blank=True, null=True)
    updated = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'specific_price'
        verbose_name_plural = 'specific_prices'

    def compare(self, product):
        result = {}
        if self.dto_percent != product.dto_percent:
            result['dto_percent'] = product.dto_percent
        return result

    def update_discount(self):
        return {
            "specific_prices": {
                "id": self.ps_id,
                "reduction": str(float(self.dto_percent/100)),
                "id_shop": 0,
                "id_cart": 0,
                "id_product": self.combination_id.product_id.ps_id,
                "id_product_attribute": self.combination_id.ps_id,
                "id_currency": 0,
            }
        }

    def create_discount(self):
        return {
            "specific_prices": {
                "reduction": str(float(self.dto_percent/100)),
                "id_product": self.combination_id.product_id.ps_id,
                "id_product_attribute": self.combination_id.ps_id,
                "id_shop": 0,
                "id_cart": 0,
                "id_currency": 0,
                "id_country": 0,
                "id_group": 0,
                "id_customer": 0,
                "price": 0,
                "reduction_tax": 0,
                "from": '0000-00-00 00:00:00',
                "to": '0000-00-00 00:00:00',
                "reduction_type": 'percentage',
                "from_quantity": 1,
            }
        }

# vim: et ts=4 sw=4
