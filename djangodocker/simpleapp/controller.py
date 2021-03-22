# -*- coding: utf-8 -*-
import prestapyt
from . import models, mssql, constants
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
from django.utils.timezone import now
from datetime import datetime
import logging
from django.utils.timezone import make_aware

class ControllerICGProducts(object):
    def __init__(self, url_base=''):
        self._url_base = url_base
        self.logger = logging.getLogger(__name__)

    def escapeSpecialChars(self, name):
        return name.replace("{","").replace("}","").replace("'","")

    def get_create_or_update(self, obj_name, primary_key, other_fields={}):
        dj_object = getattr(models, obj_name)
        create = dict(primary_key, **other_fields)
        m_new = dj_object(**create)
        try:
            m_old = dj_object.objects.get(**primary_key)
            updated = m_old.compareICG(m_new)
            if updated:
                updated['fields_updated'] = updated.copy()
                updated['updated'] = True
                updated['modified_date'] = now()
                dj_object.objects.filter(pk=m_old.pk).update(**updated)
                self.logger.info("Objecte '%s' modificada: %s", str(dj_object), str(updated))
            if m_old.ps_id == 0:
                m_old.updated=True
                m_old.save()
            return m_old
        except ObjectDoesNotExist:
            m_new.updated = True
            m_new.save()
            self.logger.info("Objecte creada %s:%d" % (str(dj_object), m_new.pk))
            return m_new
        except MultipleObjectsReturned:
            self.logger.error("Objecte torna més d'un: %s",
                str(dj_object.objects.filter(**primary_key)))


    def saveNewProducts(self, url_base=None, data=None):
        if not url_base:
            url_base = self._url_base
        ms = mssql.MSSQL()
        np  = ms.newProducts(url_base, data)
        ean13 = ''
        for index,row in np.iterrows():
            icg_id = row[0]
            icg_reference = row[1]
            icg_talla = self.escapeSpecialChars(row[2])
            icg_color = self.escapeSpecialChars(row[3])
            if row[4]:
                ean13 = row[4]
            icg_name = row[6]
            iva = row[8]
            icg_modified_date = make_aware(datetime.strptime(row[11], '%Y-%m-%d %H:%M:%S'))
            visible_web = True if row[12] == 'T' else False
            manufacturer_id = row[13]
            discontinued = True if row[15] == 'T' else False
            
            man = self.get_create_or_update('Manufacturer', 
                {'icg_id': manufacturer_id}, {'icg_name': row[14] })

            prod = self.get_create_or_update('Product', {'icg_id': icg_id},
                {'icg_reference': icg_reference, 'icg_name': icg_name, 'visible_web': visible_web,
                 'manufacturer': man, 'icg_modified_date': icg_modified_date})

            comb = self.get_create_or_update('Combination', {'product_id': prod,
                'icg_color': icg_color, 'icg_talla': icg_talla},
                {'discontinued': discontinued, 'ean13': ean13})

            price_exist = models.Price.objects.filter(combination_id = comb)
            if not price_exist:
                price = self.get_create_or_update('Price', {'combination_id': comb}, {})
                price.updateFromICG()

            stock_exist = models.Stock.objects.filter(combination_id = comb)
            if not stock_exist:
                stock = self.get_create_or_update('Stock', {'combination_id': comb}, {})
                stock.updateFromICG()

            sp_exist = models.SpecificPrice.objects.filter(combination_id = comb, product_id = prod)
            if not sp_exist:
                spec_price = self.get_create_or_update('SpecificPrice',
                    {'combination_id': comb, 'product_id': prod},{})
                spec_price.updateFromICG()

    def saveNewPrices(self, url_base=None, data=None):
        if not url_base:
            url_base = self._url_base
        ms = mssql.MSSQL()
        np  = ms.newPrices(url_base, data)
        for index,row in np.iterrows():
            icg_id = row[1]
            icg_talla = self.escapeSpecialChars(row[2])
            icg_color = self.escapeSpecialChars(row[3])
            dto_percent = row[5]
            iva = row[8]
            pvp_siva = row[9]
            #'2020-01-20 16:55:35'
            icg_modified_date = make_aware(datetime.strptime(row[12], '%Y-%m-%d %H:%M:%S'))

            prod = self.get_create_or_update('Product', {'icg_id': icg_id},{})
            if not prod.icg_reference:
                prod.updateFromICG()
            comb = self.get_create_or_update('Combination', {'product_id': prod,
                'icg_color': icg_color, 'icg_talla': icg_talla},{})
            price = self.get_create_or_update('Price', {'combination_id': comb}, {'iva': iva,
                'pvp_siva': pvp_siva, 'icg_modified_date': icg_modified_date})

            if dto_percent:
                spec_price = self.get_create_or_update('SpecificPrice', {'combination_id': comb},
                    {'dto_percent': dto_percent, 'icg_modified_date': icg_modified_date, 'product_id': prod})
                spec_price.updateFromICG()


    def saveNewStocks(self, url_base=None, data=None):
        if not url_base:
            url_base = self._url_base
        ms = mssql.MSSQL()
        np = ms.newStocks(url_base, data)
        for index,row in np.iterrows():
            icg_id = row[0]
            icg_talla = self.escapeSpecialChars(row[1])
            icg_color = self.escapeSpecialChars(row[2])
            icg_stock = row[7]
            icg_modified_date = make_aware(datetime.strptime(row[8], '%Y-%m-%d %H:%M:%S'))
            prod = self.get_create_or_update('Product', {'icg_id': icg_id},{})
            if not prod.icg_reference:
                prod.updateFromICG()
            comb = self.get_create_or_update('Combination', {'product_id': prod,
                'icg_color': icg_color, 'icg_talla': icg_talla},{})
            stock = self.get_create_or_update('Stock', {'combination_id': comb},
                {'icg_stock': icg_stock, 'icg_modified_date': icg_modified_date})

    def updateDataFromICG(self):
        ps_prod = []
        #updated_products = models.Product.objects.filter(icg_reference = '')
        updated_products = models.Product.objects.filter(updated = True)
        for prod in updated_products:
            prod.updateFromICG()
            ps_prod.append(prod.icg_reference)

        ps_comb = []
        updated_comb = models.Combination.objects.filter(updated = True)
        for comb in updated_comb:
            comb.updateFromICG()
            ps_comb.append(comb.product_id.icg_reference)

        updated = updated_products or updated_comb
        return updated, {'ps_prod': ps_prod, 'ps_comb': ps_comb}

    def updateManufacturerFromICG(self, man):
        ms = mssql.MSSQL()
        result = ms.getManufacturerData(constants.URLBASE, man.ps_name)
        if isinstance(result, bool):
           return False
        for index,row in result.iterrows():
           man.icg_id = row[13]
           man.icg_name = row[14]
           man.updated = False
           man.save()
        return True

    def updateProductFromICG(self, prod):
        ms = mssql.MSSQL()
        result = ms.getProductData(constants.URLBASE, prod.icg_reference)
        if isinstance(result, bool):
            return False
        for index,row in result.iterrows():
            prod.icg_id = row[0]
            prod.icg_reference = row[1]
            prod.icg_name = row[6]
            prod.icg_modified_date = make_aware(datetime.strptime(row[11], '%Y-%m-%d %H:%M:%S'))
            prod.updated = False
            prod.save()
        return True

    def updateCombinationFromICG(self, comb):
        ms = mssql.MSSQL()
        result = ms.getCombinationData(constants.URLBASE, comb.product_id.icg_reference,
            comb.icg_talla, comb.icg_color)
        if isinstance(result, bool):
            return False
        for index,row in result.iterrows():
            comb.icg_talla = self.escapeSpecialChars(row[2])
            comb.icg_color = self.escapeSpecialChars(row[3])
            if row[4]:
                comb.ean13 = row[4]
            comb.discontinued = True if row[15] == 'T' else False
            comb.updated = False
            comb.save()
        return True

    def updateStockFromICG(self, stock):
        ms = mssql.MSSQL()
        result = ms.getStockData(constants.URLBASE, stock.combination_id.product_id.icg_id,
            stock.combination_id.icg_talla, stock.combination_id.icg_color)
        if isinstance(result, bool):
            return False
        for index,row in result.iterrows():
            stock.icg_stock = row[7]
            stock.icg_modified_date = make_aware(datetime.strptime(row[8], '%Y-%m-%d %H:%M:%S'))
            stock.updated = False
            stock.save()
        return True

    def updatePriceFromICG(self, price):
        ms = mssql.MSSQL()
        result = ms.getPriceData(constants.URLBASE, price.combination_id.product_id.icg_id,
            price.combination_id.icg_talla, price.combination_id.icg_color)
        if isinstance(result, bool):
            return False
        for index,row in result.iterrows():
            price.iva = row[8]
            price.pvp_siva = row[9]
            price.icg_modified_date = make_aware(datetime.strptime(row[12], '%Y-%m-%d %H:%M:%S'))
            price.pvp = row[4]
            price.preu_oferta = float(row[4]) - float(row[7])
            price.preu_oferta = row[10]
            price.updated = False
            price.save()
        return True

    def updateSpecificPriceFromICG(self, sp):
        ms = mssql.MSSQL()
        if sp.product_id:
            result = ms.getDiscountData(constants.URLBASE, sp.product_id.icg_id,
                sp.combination_id.icg_talla, sp.combination_id.icg_color)
        else:
            result = ms.getDiscountData(constants.URLBASE, sp.combination_id.product_id.icg_id,
                sp.combination_id.icg_talla, sp.combination_id.icg_color)
        if isinstance(result, bool):
            return False
        for index,row in result.iterrows():
            sp.dto_percent = row[5]
            sp.icg_modified_date = make_aware(datetime.strptime(row[12], '%Y-%m-%d %H:%M:%S'))
            if not sp.product_id:
                sp.product_id = self.get_create_or_update('Product', {'icg_id': row[1]})
            sp.updated = False
            sp.save()
        return True


# vim: et ts=4 sw=4
