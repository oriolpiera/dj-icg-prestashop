# -*- coding: utf-8 -*-
import prestapyt
from . import models, mssql
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
from django.utils.timezone import now
from datetime import datetime
import logging
from django.utils.timezone import make_aware
#import pytz

class ControllerICGProducts(object):
    def __init__(self, url_base=''):
        self._url_base = url_base
        self.logger = logging.getLogger(__name__)


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
            return m_old
        except ObjectDoesNotExist:
            m_new.save()
            self.logger.info("Objecte creada %s", str(dj_object))
            return m_new
        except MultipleObjectsReturned:
            self.logger.error("Objecte torna més d'un: %s", +
                str(dj_object.objects.filter(**primary_key)))


    def saveNewProducts(self, url_base=None, data=None):
        if not url_base:
            url_base = self._url_base
        ms = mssql.MSSQL()
        np  = ms.newProducts(url_base, data)
        for index,row in np.iterrows():
            icg_id = row[0]
            icg_reference = row[1]
            icg_talla = row[2]
            icg_color = row[3]
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


    def saveNewPrices(self, url_base=None, data=None):
        if not url_base:
            url_base = self._url_base
        ms = mssql.MSSQL()
        np  = ms.newPrices(url_base, data)
        for index,row in np.iterrows():
            icg_id = row[1]
            icg_talla = row[2]
            icg_color = row[3]
            dto_percent = row[5]
            iva = row[8]
            pvp_siva = row[9]
            #'2020-01-20 16:55:35'
            icg_modified_date = make_aware(datetime.strptime(row[12], '%Y-%m-%d %H:%M:%S'))

            prod = self.get_create_or_update('Product', {'icg_id': icg_id},{})
            comb = self.get_create_or_update('Combination', {'product_id': prod,
                'icg_color': icg_color, 'icg_talla': icg_talla},{})
            price = self.get_create_or_update('Price', {'combination_id': comb}, {'iva': iva,
                'pvp_siva': pvp_siva, 'icg_modified_date': icg_modified_date})

            if dto_percent:
                spec_price = self.get_create_or_update('SpecificPrice', {'combination_id': comb},
                    {'dto_percent': dto_percent, 'icg_modified_date': icg_modified_date})


    def saveNewStocks(self, url_base=None, data=None):
        if not url_base:
            url_base = self._url_base
        ms = mssql.MSSQL()
        np = ms.newStocks(url_base, data)
        for index,row in np.iterrows():
            icg_id = row[0]
            icg_talla = row[1]
            icg_color = row[2]
            icg_stock = row[7]
            icg_modified_date = make_aware(datetime.strptime(row[8], '%Y-%m-%d %H:%M:%S'))
            prod = self.get_create_or_update('Product', {'icg_id': icg_id},{})
            comb = self.get_create_or_update('Combination', {'product_id': prod,
                'icg_color': icg_color, 'icg_talla': icg_talla},{})
            stock = self.get_create_or_update('Stock', {'combination_id': comb},
                {'icg_stock': icg_stock, 'icg_modified_date': icg_modified_date})

    def updateDataFromICG(self):
        ps_prod = []
        updated_products = models.Product.objects.filter(icg_reference = '')
        for prod in updated_products:
            prod.updateFromICG()
            ps_prod.append(prod.icg_reference)

        ps_comb = []
        updated_comb = models.Combination.objects.filter(updated = True, ean13='')
        for comb in updated_comb:
            comb.updateFromICG()
            ps_comb.append(comb.product_id.icg_reference)

        updated = updated_products or updated_comb
        return updated, {'ps_prod': ps_prod, 'ps_comb': ps_comb}

# vim: et ts=4 sw=4
