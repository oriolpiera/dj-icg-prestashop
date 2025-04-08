# -*- coding: utf-8 -*-
from djangodocker.simpleapp.models import *

# Clean duplicated combinations in Prestasho

print(len(Combination.objects.values('product_id', 'icg_talla', 'icg_color').annotate(cnt=models.Count('id')).filter(cnt__gt=1)))
comb_list = Combination.objects.values('product_id', 'icg_talla', 'icg_color').annotate(cnt=models.Count('id')).filter(cnt__gt=1)
for comb in comb_list:
    comb.pop('cnt')
    dup_list = Combination.objects.filter(**comb)
    for dup in dup_list[1:]:
        dup.discontinued = True
        dup.updated = True
        dup.save()
        print(dup)
    #break
print("Done")
# After updated to Prestashop (5 minutes)
#Combination.objects.all().filter(ps_id = 0, discontinued=True).delete()

# vim: et ts=4 sw=4
