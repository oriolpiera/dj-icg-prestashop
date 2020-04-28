# -*- coding: utf-8 -*-
import prestapyt
from . import models, mssql
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
import datetime
import logging

class ControllerICGProducts(object):
    def __init__(self, url_base=''):
        self._url_base = url_base
        self.logger = logging.getLogger(__name__)


    def get_create_or_update_manufacturer(self, manufacturer_id, manufacturer_name):
        #Manufacturer exist
        man = None
        m_old = None
        m_new = models.Manufacturer(icg_id = manufacturer_id,
            icg_name = manufacturer_name)
        try:
            m_old = models.Manufacturer.objects.get(icg_id = manufacturer_id)
            man = m_old
        except ObjectDoesNotExist:
            self.logger.info("Marca creada %s", str(manufacturer_id))
            m_new.save()
            man = m_new

        if m_old and m_old.icg_name != manufacturer_name:
            self.logger.info("Canviem el nom de la Marca %s > %s" % (str(m_old.icg_name), str(manufacturer_name)))
            m_old.icg_name = manufacturer_name
            m_old.modified_date = datetime.datetime.now()
            m_old.updated = True

        return man


    def get_create_or_update_product(self, icg_id, icg_reference, icg_name, visible_web, man):
        #Product
        prod = None
        p_new = models.Product(icg_id = icg_id, icg_reference = icg_reference,
            icg_name = icg_name, visible_web = visible_web, manufacturer = man)
        try:
            p_old = models.Product.objects.get(icg_id = icg_id)
            prod_pk = p_old.pk
            updated = p_old.compare(p_new)
            if updated:
                models.Product.objects.filter(pk=p_old.pk).update(**updated)
                self.logger.info("Producte modificat: %s", str(updated))
            prod = p_old
        except ObjectDoesNotExist:
            self.logger.info("Producte creat: %s", str(icg_id))
            p_new.save()
            p_old = p_new

            prod_pk = p_new.pk
            prod = p_new
        except MultipleObjectsReturned:
            self.logger.error("Producte torna més d'un: %s", str(models.Product.objects.filter(icg_id = icg_id)))

        return prod

    def get_create_or_update_product_option(self, ps_name, product):
        #Product Option (Grup talla color)
        po = None
        po_new = models.ProductOption.create(ps_name, product)
        try:
            po_old = models.ProductOption.objects.get(ps_name = ps_name, product_id = product)
            print("Hem fet un GET! " + str(ps_name))
            return po_old
        except ObjectDoesNotExist:
            po_new.save()
            self.logger.info("Producte option creat: %s", str(product.icg_id))
            return po_new
        except MultipleObjectsReturned:
            self.logger.error("Product option torna més d'un: %s", str(models.ProductOption.objects.filter(ps_name = ps_name, product_id = product)))


    def get_create_or_update_combination(self, product_id, icg_color, icg_talla, discontinued, ean13):
        #Combination
        comb = None

        c_new = models.Combination(product_id = product_id, icg_color = icg_color,
            icg_talla = icg_talla, discontinued = discontinued, ean13 = ean13)
        try:
            c_old = models.Combination.objects.get(product_id = product_id,
                icg_talla = icg_talla, icg_color = icg_color)
            updated = c_old.compare(c_new)
            if updated:
                models.Combination.objects.filter(pk=c_old.pk).update(**updated)
                self.logger.info("Combinació modificada: %s", str(updated))
            comb = c_old
        except ObjectDoesNotExist:
            self.logger.info("Combinació creada: %s - %s - %s" %
                (str(c_new.product_id.icg_id), str(icg_talla), str(icg_color)))
            c_new.save()
            comb = c_new
        except MultipleObjectsReturned:
            self.logger.error("Combinació torna més d'un: %s",
                str(models.Combination.objects.filter(product_id = prod_pk,
                icg_talla = icg_talla, icg_color = icg_color)))

        return comb


    def saveNewProducts(self, url_base=None):
        if not url_base:
            url_base = self._url_base
        ms = mssql.MSSQL()
        np  = ms.newProducts(url_base)
        for index,row in np.iterrows():
            icg_id = row[0]
            icg_reference = row[1]
            icg_talla = row[2]
            icg_color = row[3]
            ean13 = row[4]
            icg_name = row[6].encode('utf-8')
            iva = row[8]
            #icg_modified_date = row[11]
            visible_web = True if row[12] == 'T' else False
            manufacturer_id = row[13]
            discontinued = True if row[15] == 'T' else False
            
            #Django pk
            man_pk = None
            prod_pk = None

            man = self.get_create_or_update_manufacturer(manufacturer_id, row[14])
            man_pk = man.pk

            prod = self.get_create_or_update_product(icg_id, icg_reference, icg_name,
                visible_web, man)


            comb = self.get_create_or_update_combination(prod, icg_color, icg_talla, discontinued, ean13)


class ControllerICGPrices(object):
    def __init__(self, url_base=''):
        self._url_base = url_base
        self.logger = logging.getLogger(__name__)


    def get_create_or_update_product(self, icg_id):
        return models.Product.objects.get(icg_id = icg_id)


    def get_create_or_update_combination(self, product_id, icg_color, icg_talla):
        return models.Combination.objects.get(product_id = product_id, icg_color = str(icg_color),
             icg_talla = str(icg_talla))


    def get_create_or_update_price(self, combination_id, dto_percent, iva, pvp_siva):
        comb = None
        pc_new = models.Price(combination_id = combination_id, dto_percent = dto_percent,
            iva = iva, pvp_siva=pvp_siva)

        try:
            pc_old = models.Price.objects.get(combination_id = combination_id)
            updated = pc_old.compare(pc_new)
            if updated:
                models.Price.objects.filter(pk=pc_old.pk).update(**updated)
                self.logger.info("Preu modificat: %s", str(updated))
            comb = pc_old
        except ObjectDoesNotExist:
            self.logger.error("Preu creat: %s ", str(combination_id))
            pc_new.save()
            comb = pc_new
        except MultipleObjectsReturned:
            self.logger.error("Preu torna més d'un: %s",
                str(models.Price.objects.filter(combination_id = combination_id)))
            raise MultipleObjectsReturned(e)

        return comb


    def saveNewPrices(self, url_base=None):
        if not url_base:
            url_base = self._url_base
        ms = mssql.MSSQL()
        np  = ms.newPrices(url_base)
        for index,row in np.iterrows():
            icg_id = eval(row[1])
            icg_talla = row[2].strip('\"')
            icg_color = row[3].strip('\"')
            dto_percent = eval(row[5])
            iva = eval(row[8])
            pvp_siva = eval(row[9])
            #icg_modified_date = row[12]

            prod = self.get_create_or_update_product(icg_id)
            comb = self.get_create_or_update_combination(prod, icg_color, icg_talla)
            comb2 = self.get_create_or_update_price(comb, dto_percent, iva, pvp_siva)



class ControllerICGStocks(object):
    def __init__(self, url_base=''):
        self._url_base = url_base
        self.logger = logging.getLogger(__name__)


    def get_create_or_update_product(self, icg_id):
        return models.Product.objects.get(icg_id = icg_id)


    def get_create_or_update_combination(self, product_id, icg_color, icg_talla):
        return models.Combination.objects.get(product_id = product_id, icg_color = str(icg_color),
             icg_talla = str(icg_talla))


    def get_create_or_update_stock(self, combination_id, icg_stock):
        stock = None
        try:
            stock = models.Stock.objects.get(combination_id = combination_id)
            self.logger.info("Stock modificat de %d: %s", combination_id.pk, str(icg_stock))
            stock.icg_stock = icg_stock
            stock.save()
        except ObjectDoesNotExist:
            stock = models.Stock(combination_id = combination_id, icg_stock = icg_stock)
            self.logger.error("Stock creat: %s ", str(combination_id))
            stock.save()
        except MultipleObjectsReturned as e:
            self.logger.error("Stock torna més d'un: %s",
                str(models.Price.objects.filter(combination_id = combination_id)))
            raise MultipleObjectsReturned(e)

        return stock


    def saveNewStocks(self, url_base=None):
        if not url_base:
            url_base = self._url_base
        ms = mssql.MSSQL()
        np = ms.newStocks(url_base)
        for index,row in np.iterrows():
            icg_id = eval(row[0])
            icg_talla = row[1].strip('\"')
            icg_color = row[2].strip('\"')
            icg_stock = eval(row[7])
            #icg_modified_date = row[8]

            prod = self.get_create_or_update_product(icg_id)
            comb = self.get_create_or_update_combination(prod, icg_color, icg_talla)
            comb2 = self.get_create_or_update_stock(comb, icg_stock)

# vim: et ts=4 sw=4
