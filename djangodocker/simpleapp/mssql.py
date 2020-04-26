# -*- coding: utf-8 -*-
import pandas as pd
import os

class MSSQL(object):
    def newProducts(self, urlbase):
        # Products line
        # CODARTICULO	Referencia	TALLA	COLOR	CODBARRAS	CODBARRAS2	DESCRIPCION	Tipo_impuesto	IVA	Codproveedor	Nombre_Proveedor	Fecha_Modificado	Visible_Web	Codigo_Marca	Descripcion_Marca	DESCATALOGADO
        # 7500;0930095;12;"CAR 12 ML";8712079312930;8712079312800;"Caja Témpera ArtCreation";1;21;93;"TALENS ESPAÑA S.A.U.";"2020-01-29 13:36:12";T;14000;ARTECREATION;F;

        filename = 'csvNousProductes.php'
        if urlbase:
            filename = urlbase + filename
        else:
            filename = os.path.join(os.path.dirname(__file__), filename)
        data = pd.read_csv(filename, delimiter=";", encoding="utf-8", header=None)
        return data


    def newPrices(self, urlbase):
        # Prices line
        # Tarifa	Codarticulo	Talla	Color	Pbruto_iva	Dto_porc	Pneto_iva	Dto_impote_iva	Iva	Pbruto_s_iva	Pneto_s_iva	Dto_importe_s_iva	Fecha_modificado
        # """1""","""7498""","""***""","""***""","""135.45""","""30""","""94.815""","""40.635""","""21""","""111.94""","""78.36""","""33.58""","""2020-01-20 16:55:35"""

        filename = 'csvNousPreus.php'
        if urlbase:
            filename = urlbase + filename
        else:
            filename = os.path.join(os.path.dirname(__file__), filename)
        data = pd.read_csv(filename, delimiter=",", encoding="utf-8", header=None)
        return data

    def newStocks(self, urlbase):
        # Stock line
        # Codarticulo	Talla	Color	Codalmacen	Nombre_alm	Stock_real	Stock_Aservir	Stock_disponible	Fecha_Modificado
        # """7498""","""***""","""***""","""01""","""Pintor Fortuny""","""5""","""0""","""5""","""2020-03-06 19:24:47"""
        filename = 'csvNousStocsk.php'
        if urlbase:
            filename = urlbase + filename
        else:
            filename = os.path.join(os.path.dirname(__file__), filename)
        data = pd.read_csv(filename, delimiter=",", encoding="utf-8", header=None)
        return data

# vim: et ts=4 sw=4
