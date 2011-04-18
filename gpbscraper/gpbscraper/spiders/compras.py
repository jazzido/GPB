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

import django.db.backends.postgresql_psycopg2

class ComprasSpider(BaseSpider):
    name = 'compras'
    allowed_domains = ['bahiablanca.gov.ar']

    anio = settings.get('ANIO', datetime.now().year)
    fecha_desde = settings.get('FECHA_DESDE', datetime(datetime.now().year, datetime.now().month, 1).strftime('%d/%m/%Y'))
    fecha_hasta = settings.get('FECHA_HASTA', datetime.now().strftime('%d/%m/%Y'))

    start_urls = ['http://www.bahiablanca.gov.ar/compras4/comprasrV2.asp?ejercicio=%s&desde=%s&hasta=%s&title=&SUBMIT1=Buscar&page=1' % (anio, fecha_desde, fecha_hasta)]

    def parse_compra_items(self, response):
        orden_compra = response.request.meta['compra']
        hxs = HtmlXPathSelector(response)
        for tr in hxs.select('//table[contains(@width, "760")][2]/tr'):
            i = CompraLineaItem()
            l = XPathItemLoader(item=i, selector=tr)
            l.add_xpath('cantidad', 'td[1]/text()')
            l.add_xpath('importe', 'td[2]/text()')
            l.add_xpath('detalle', 'td[3]/text()')
            x = l.load_item()
            
            orden_compra['compra_linea_items'].append(x)
        
        yield orden_compra

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        for tr in hxs.select('//div[@id="miListView"]/table/tr'):
            i = CompraItem()
            l = XPathItemLoader(item=i, selector=tr)
            l.add_xpath('orden_compra', 'td[1]/text()')
            l.add_xpath('fecha', 'td[2]/text()')
            l.add_xpath('importe', 'td[3]/text()')
            l.add_xpath('suministro', 'td[4]/text()')
            l.add_xpath('proveedor', 'td[5]/text()')
            l.add_xpath('destino', 'td[6]/text()')

            compra_detalle_url = urljoin(response.url, tr.select('td[7]/a/@href').extract()[0])
            req = Request(compra_detalle_url, 
                          callback=self.parse_compra_items)

            compra = l.load_item()
            compra['compra_linea_items'] = []

            req.meta['compra'] = l.load_item()
            
            yield req

        for url in hxs.select('//a[contains(@href, "/compras4/comprasrV2")]/@href').extract():
            yield Request(urljoin(response.url, url), callback=self.parse)

SPIDER = ComprasSpider()
