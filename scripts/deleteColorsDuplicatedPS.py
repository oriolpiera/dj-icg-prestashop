# -*- coding: utf-8 -*-
from djangodocker.simpleapp.models import *

# Clean attributes (colors) in Prestashop thant not exist in Django
comb_zero = p._api.get('product_option_values')
per_esborrar = [] 
for r in comb_zero['product_option_values']['product_option_value']:
    exist = ProductOptionValue.objects.filter(ps_id=r['attrs']['id'])
    if not exist:
        per_esborrar.append(r['attrs']['id'])
        print("Nooo exist: " + str(r['attrs']['id']))
    if len(per_esborrar) == 20:
        r_delete = p._api.delete('product_option_values', resource_ids=per_esborrar)
        print("Esborro: " + str(per_esborrar))
        per_esborrar = []
        time.sleep(3)

print("Esborro: " + str(per_esborrar))
r_delete = p._api.delete('product_option_values', resource_ids=per_esborrar)


# Clean attribute_groups in Presatshop that not exist in Django

comb_zero = p._api.get('product_options')

per_esborrar = []
for r in comb_zero['product_options']['product_option']:
    exist = ProductOption.objects.filter(ps_id=r['attrs']['id'])
    if not exist:
        per_esborrar.append(r['attrs']['id'])
        print("Nooo exist: " + str(r['attrs']['id']))
    if len(per_esborrar) == 20:
        r_delete = p._api.delete('product_options', resource_ids=per_esborrar)
        print("Esborro: " + str(per_esborrar))
        per_esborrar = []
        time.sleep(2)

print("Esborro: " + str(per_esborrar))
r_delete = p._api.delete('product_options', resource_ids=per_esborrar)


# After updated to Prestashop (5 minutes)
#Combination.objects.all().filter(ps_id = 0, discontinued=True).delete()


# vim: et ts=4 sw=4
