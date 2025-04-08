# -*- coding: utf-8 -*-
from djangodocker.simpleapp.models import *

for p in ProductOptionValue.objects.all():
    pov = ProductOptionValue.objects.filter(ps_name=p.ps_name, po_id=p.po_id)
    if len(pov) > 1:
        print("Més d'un " + str(pov))
        ps_id = pov[0].ps_id
        for pc in pov:
            if pc.ps_id == ps_id:
                comb = Combination.objects.filter(talla_id=pc.id)
                comb2 = Combination.objects.filter(color_id=pc.id)
                if comb or comb2:
                    print("No eliminem, existeix combinacio: ")
                    continue
                try:
                    print("Eliminar " + str(pc))
                    pc.delete()
                except:
                    continue
    else:
        print("Un " + str(pov))

