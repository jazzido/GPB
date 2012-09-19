import urllib
import xml.etree.ElementTree as xml
from datetime import datetime
import re

from scrapy.conf import settings
from scrapy.http import Request
from scrapy.spider import BaseSpider

from gpbscraper.items import CompraItem, CompraLineaItem


BASE_URL = 'http://www.bahiablanca.gov.ar/wsMBB/compras.asmx/ComprasRealizadas?'
OC_DETAIL_BASE_URL = 'http://www.bahiablanca.gov.ar/wsMBB/compras.asmx/DetalleOrdenCompra?'

class ComprasSpiderWS(BaseSpider):

    name = 'compras_ws'
    allowed_domains = ['bahiablanca.gov.ar']

    fecha_desde = settings.get('FECHA_DESDE', datetime(datetime.now().year, datetime.now().month, 1).strftime('%d/%m/%Y'))
    fecha_hasta = settings.get('FECHA_HASTA', datetime.now().strftime('%d/%m/%Y'))
    anio = settings.get('ANIO', settings.get('FECHA_DESDE', datetime(datetime.now().year, datetime.now().month, 1).strftime('%d/%m/%Y')).split('/')[2])
    key = settings.get('KEY', None)


    def start_requests(self):
        if self.key is None: raise Exception("KEY cannot be None")

        return [Request(BASE_URL + urllib.urlencode({
                        'Key': self.key,
                        'Anio': self.anio,
                        'FechaDesde': self.fecha_desde,
                        'FechaHasta': self.fecha_hasta,
                        'Proveedor': '*'
                        }),
                        callback=self.getOCs)]

    def getOCs(self, response):

        root = xml.fromstring(response.body)

        for cr in root[1][0].getchildren():
            req = Request(OC_DETAIL_BASE_URL + urllib.urlencode({'Key': 
                                                                 self.key, 
                                                                 'Anio': self.anio, 
                                                                 'OrdenCompra': cr.find('ORDENCOMPRA').text}),
                          callback=self.getOCDetalle)

            item = CompraItem()
            item['orden_compra'] = cr.find('ORDENCOMPRA').text
            item['fecha'] = datetime.strptime(cr.find('FECHA').text, '%Y-%m-%dT%H:%M:%S-03:00') \
                             .strftime('%Y-%m-%d')
            item['importe'] = cr.find('IMPORTE').text
            item['proveedor'] = cr.find('PROVEEDOR').text
            item['destino'] = cr.find('DEPENDENCIA').text
            
            tipo, suministro, anio = re.search("(.+) (\d+)/(\d+)", cr.find('EXPEDIENTE').text).groups()
            item['anio'] = anio
            item['tipo'] = tipo
            item['suministro'] = suministro

            item['compra_linea_items'] = []

            req.meta['compra'] = item

            yield req


    def getOCDetalle(self, response):
        
        root = xml.fromstring(response.body)

        orden_compra = response.request.meta['compra']

        for oc_detalle in root[1][0].getchildren():
            l = CompraLineaItem()
            l['cantidad'] = oc_detalle.find('CANTIDAD').text
            l['unidad_medida'] = oc_detalle.find('UNIDADMEDIDA').text
            l['detalle'] = oc_detalle.find('DETALLE').text
            l['importe'] = oc_detalle.find('IMPORTEUNITARIO').text

            orden_compra['compra_linea_items'].append(l)

            yield orden_compra

SPIDER = ComprasSpiderWS()
