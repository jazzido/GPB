import urllib
import xml
import xml.etree.ElementTree as xml
from datetime import datetime

from scrapy.conf import settings
from scrapy.http import Request

from gpbscraper.items import CompraItem, CompraLineaItem


BASE_URL = 'http://www.bahiablanca.gov.ar/wsMBB/compras.asmx/ComprasRealizadas?'
OC_DETAIL_BASE_URL = 'http://www.bahiablanca.gov.ar/wsMBB/compras.asmx/DetalleOrdenCompra?'

class ComprasSpiderWS(BaseSpider):

    name = 'compras_ws'
    fecha_desde = settings.get('FECHA_DESDE', datetime(datetime.now().year, datetime.now().month, 1).strftime('%d/%m/%Y'))
    fecha_hasta = settings.get('FECHA_HASTA', datetime.now().strftime('%d/%m/%Y'))
    anio = settings.get('ANIO', settings.get('FECHA_DESDE', datetime(datetime.now().year, datetime.now().month, 1).strftime('%d/%m/%Y')).split('/')[2])
    key = settings.get('KEY', None)


    def start_requests(self):
        if self.key is None: raise Execption("KEY cannot be None")

        return [Request(BASE_URL + urllib.urlencode({
                        'Key': self.key,
                        'Ejercicio': self.anio,
                        'Desde': self.fecha_desde,
                        'Hasta': self.fecha_hasta,
                        'Fantasia': '*'
                        }),
                        callback=self.getOCs)]

    def getOCs(sef, response):
        root = xml.etree.ElementTree.fromstring(response.body).getroot()

#        Key=5a246e6932c6e05f025764d502104501b9171563&Ejercicio=2012&Nro_OC=2731
        for cr in root[1][0].getchildren():
            req = Request(OC_DETAIL_BASE_URL + urllib.urlencode({'Key': 
                                                                 self.key, 
                                                                 'Ejercicio': self.anio, 
                                                                 'Nro_OC': cr.find('NRO_OC').text}),
                          callback=self.getOCDetalle)
            item = CompraItem()
            item['orden_compra'] = cr.find('NRO_OC').text
            item['fecha'] = datetime.strptime(cr.find('FECH_OC').text, '%Y-%m-%dT%H:%M:%S-03:00') \
                             .strftime('%d/%m/%Y')
            item['importe'] = cr.find('IMPORTE_TOT').text
            item['proveedor'] = cr.find('FANTASIA').text
            item['destino'] = cr.find('DEP_DESCRIPCION').text
            item['suministro'] = cr.find('NRO_DOC_RES').text
            item['anio'] = cr.find('ANIO_DOC_RES').text
            item['tipo'] = cr.find('TIPO_DOC_RES_DESC').text
            item['compra_linea_items'] = []

            req.meta['compra'] = item

            yield req


    def getOCDetalle(self, response):
        
        root = xml.etree.ElementTree.fromstring(response.body).getroot()

        orden_compra = response.request.meta['compra']

        for oc_detalle in root[1][0].getchildren():
            l = CompraLineaItem()
            l['cantidad'] = oc_detalle.find('CANTIDAD').text
            l['unidad_medida'] = oc_detalle('UM').text
            l['detalle'] = oc_detalle.find('DETALLE').text
            l['importe'] = oc_detalle.find('IMP_UNITARIO').text

            orden_compra['compra_linea_items'].append(l)

