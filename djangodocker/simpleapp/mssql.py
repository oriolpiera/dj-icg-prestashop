# -*- coding: utf-8 -*-
import pandas as pd
import os
import requests
from .constants  import *
import io

class MSSQL(object):
    def newProducts(self, urlbase, data=None):
        # Products line
        # CODARTICULO;Referencia;TALLA;COLOR;CODBARRAS;CODBARRAS2;DESCRIPCION;Tipo_impuesto;IVA;Codproveedor;Nombre_Proveedor;Fecha_Modificado;Visible_Web;Codigo_Marca;Descripcion_Marca;DESCATALOGADO
        # 7500;0930095;12;"CAR 12 ML";8712079312930;8712079312800;"Caja Témpera ArtCreation";1;21;93;"TALENS ESPAÑA S.A.U.";"2020-01-29 13:36:12";T;14000;ARTECREATION;F;

        filename = 'csvNousProductes.php'
        if urlbase:
            filename = urlbase + filename
        else:
            filename = os.path.join(os.path.dirname(__file__), filename)
        if data:
            filename = io.StringIO(data)
        data = pd.read_csv(filename, delimiter=";", encoding="utf-8", header=None,
            dtype={0: 'int', 1: 'object', 4: 'object', 5: 'object' })
        return data


    def newPrices(self, urlbase, data=None):
        # Prices line
        # Tarifa;Codarticulo;Talla;Color;Pbruto_iva;Dto_porc;Pneto_iva;Dto_impote_iva;Iva;Pbruto_s_iva;Pneto_s_iva;Dto_importe_s_iva;Fecha_modificado
        # 1;7498;***;***;135.45;30;94.815;40.635;21;111.94;78.36;33.58;"2020-01-20 16:55:35"

        filename = 'csvNousPreus.php'
        if urlbase:
            filename = urlbase + filename
        else:
            filename = os.path.join(os.path.dirname(__file__), filename)
        if data:
            filename = io.StringIO(data)
        data = pd.read_csv(filename, delimiter=";", encoding="utf-8", header=None,
            dtype={1: 'int',2: 'object',3: 'object', 5: 'int'})
        return data

    def newStocks(self, urlbase, data=None):
        # Stock line
        # Codarticulo;Talla;Color;Codalmacen;Nombre_alm;Stock_real;Stock_Aservir;Stock_disponible;Fecha_Modificado
        # 7498;***;***;01;"Pintor Fortuny";5;0;5;"2020-03-06 19:24:47"

        filename = 'csvNousStocks.php'
        if urlbase:
            filename = urlbase + filename
        else:
            filename = os.path.join(os.path.dirname(__file__), filename)
        if data:
            filename = io.StringIO(data)
        data = pd.read_csv(filename, delimiter=";", encoding="utf-8", header=None)
        return data


    def getProductData(self, urlbase, icg_reference, icg_id=None):
        filename = 'getProductData.php'
        if urlbase:
            filename = urlbase + filename
        else:
            filename = os.path.join(os.path.dirname(__file__), filename)

        sql = "SELECT TOP 1 * FROM view_imp_articles WHERE Referencia = '" + icg_reference + "'"
        if icg_id:
            sql = "SELECT TOP 1 * FROM view_imp_articles WHERE CODARTICULO = " + str(icg_id)
        obj = {'token': MSSQL_TOKEN, 'sql': sql}

        result = requests.post(filename, data = obj)

        if result.status_code == 200 and result.content:
            p = result.content.decode('utf8')
            print(p)
            print("EStic aqui")
            data = pd.read_csv(io.StringIO(p), delimiter=";", encoding="utf-8", header=None,
                dtype={0: 'int', 1: 'object', 4: 'object', 5: 'object' })
            return data
        else:
            return False

    def getCombinationData(self, urlbase, icg_reference, icg_talla, icg_color):
        filename = 'getProductData.php'
        if urlbase:
            filename = urlbase + filename
        else:
            filename = os.path.join(os.path.dirname(__file__), filename)

        sql = ("SELECT TOP 1 * FROM view_imp_articles WHERE Referencia = '" + icg_reference +
            "' and TALLA = '" + icg_talla + "' and COLOR ='" + icg_color + "'")
        obj = {'token': MSSQL_TOKEN, 'sql': sql}

        result = requests.post(filename, data = obj)

        if result.status_code == 200 and result.content:
            p = result.content.decode('utf8')
            data = pd.read_csv(io.StringIO(p), delimiter=";", encoding="utf-8", header=None,
                dtype={0: 'int', 1: 'object', 4: 'object', 5: 'object' })
            return data
        else:
            return False

    def getPriceData(self, urlbase, icg_id, icg_talla, icg_color):
        filename = 'getProductData.php'
        if urlbase:
            filename = urlbase + filename
        else:
            filename = os.path.join(os.path.dirname(__file__), filename)

        sql = ("SELECT TOP 1 * FROM view_imp_preus WHERE Codarticulo = " + str(icg_id) +
            " and Talla = '" + icg_talla + "' and Color ='" + icg_color + "'")
        obj = {'token': MSSQL_TOKEN, 'sql': sql}

        result = requests.post(filename, data = obj)

        if result.status_code == 200 and result.content:
            p = result.content.decode('utf8')
            data = pd.read_csv(io.StringIO(p), delimiter=";", encoding="utf-8", header=None,
                dtype={0: 'int' })
            return data
        else:
            return False

    def getStockData(self, urlbase, icg_id, icg_talla, icg_color):
        filename = 'getProductData.php'
        if urlbase:
            filename = urlbase + filename
        else:
            filename = os.path.join(os.path.dirname(__file__), filename)

        sql = ("SELECT TOP 1 * FROM view_imp_stocks WHERE Codarticulo = " + str(icg_id) +
            " and Talla = '" + icg_talla + "' and Color ='" + icg_color + "'")
        obj = {'token': MSSQL_TOKEN, 'sql': sql}

        result = requests.post(filename, data = obj)

        if result.status_code == 200 and result.content:
            p = result.content.decode('utf8')
            data = pd.read_csv(io.StringIO(p), delimiter=";", encoding="utf-8", header=None,
                dtype={0: 'int'})
            return data
        else:
            return False

# vim: et ts=4 sw=4
