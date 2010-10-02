import re

from scrapy.conf import settings
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import XPathItemLoader
from scrapy.spider import BaseSpider
from scrapy.http import Request
from gpbscraper.items import CompraItem, CompraLineaItem
from urlparse import urljoin, urlsplit, urlparse
from datetime import datetime

# listado de proveedores
# http://www.mardelplata.gov.ar/consultas07/proveedores/navegador/listado.asp

class MDQComprasSpider(BaseSpider):
    name = 'compras'
    allowed_domains = ['mardelplata.gov.ar']

    anio = settings.get('ANIO', datetime.now().year)
    start_urls = ['http://www.mardelplata.gov.ar/Consultas07/OrdenesDeCompra/OC/index.asp']
        
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        jurisdicciones = hxs.select('//select[@name="fmJURISDICCION_CON"]/option')
        tipo_contr = hxs.select('//select[@name="fmTIPOCONT_CON"]/option')

        for j in jurisdicciones[1:]:
            for tc in tipo_contr[1:]:
                r = Request("%s?fmANIO_CON=%s&fmJURISDICCION_CON=%s&fmTIPOCONT_CON=%s&Consultar=Consultar" % \
                                (self.start_urls[0], self.anio, j.select('@value').extract()[0], tc.select('@value').extract()[0]),
                            callback=self.parse_items)

                r.meta['jurisdiccion_nombre'] = j.select('text()').extract()[0]
                r.meta['jurisdiccion_code'] = j.select('@value').extract()[0]
                r.meta['tipo_compra_nombre'] = tc.select('text()').extract()[0]
                r.meta['tipo_compra_code'] = tc.select('@value').extract()[0]

                yield r

    def parse_items(self, response):
        hxs = HtmlXPathSelector(response)
        
        dependencias = dict()
        for s in hxs.select('//div[contains(@class, "subtitle")]'):
            dependencias[s.select('input[@type="button"]/@id').extract()[0][1:]] = s.select('strong/text()').extract()[0]

        # <tr bgcolor="#EFF5FE">
        #   <td class="textocomun"><input type="button" class="input_class2" id="b" value="[VER]" onClick="VerDetalle('detalle_OC.asp?fmNRO_OC=1043&ANIO=2010',this);"></td>
        #   <td class="textocomun" align="center">1043</td>
        #   <td class="textocomun">26/7/2010</td>
        #   <td class="textocomun"><div align="right">$300,00</div></td>						
        #   <td class="textocomun">HIRSCH EDUARDO JOSE</td>
        #   <td class="textocomun">Compra Directa</td>						
        #   <td class="textocomun"></td>
        #   <td class="textocomun">Registrada</td>
        # </tr>
        i = CompraItem()
        for d, dnombre in dependencias.items():
            for c in hxs.select('//div[@id="solicitudes%s"]//tr[position() > 1]' % d):
                l = XPathItemLoader(item=i, selector=c)
                l.add_xpath('orden_compra', 'td[2]/text()')
                l.add_xpath('fecha', 'td[3]/text()')
                l.add_xpath('importe', 'td[4]/div/text()')
                l.add_value('tipo_compra', response.request.meta['tipo_compra_code'])
                l.add_value('destino', response.request.meta['jurisdiccion_nombre'])
                l.add_xpath('observaciones', 'td[7]/text()')
                l.add_xpath('proveedor', 'td[5]/text()')
                
                # examinar los renglones de esta orden
                r = Request(urljoin(response.url, c.select('td[1]/input/@onclick').re("VerDetalle\('([^']+)'")[0]),
                            callback=self.parse_lineas)
                r.meta['orden_de_compra'] = c.select('td[2]/text()').extract()[0]
                yield r

                yield l.load_item()

    def parse_lineas(self, response):
        hxs = HtmlXPathSelector(response)
        for tr in hxs.select('//table//tr[position() > 1]'):
            cli = CompraLineaItem()
            l = XPathItemLoader(item=cli, selector=tr)
            l.add_xpath('cantidad', 'td[4]/text()')
            l.add_xpath('unidad_medida', 'td[5]/text()')
            l.add_xpath('importe', 'td[3]/text()')
            l.add_xpath('importe_total', 'td[6]/text()')
            l.add_xpath('detalle', 'td[2]/text()')
            l.add_value('orden_compra', [response.request.meta['orden_de_compra']]) # hack, ver ../items.py:50 (TakeFirst())

            yield l.load_item()
            
        
        

SPIDER = MDQComprasSpider()
