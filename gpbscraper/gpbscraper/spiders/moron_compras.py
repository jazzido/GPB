# -*- coding: utf-8 -*-
import re

from scrapy.conf import settings
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import XPathItemLoader
from scrapy.spider import BaseSpider
from scrapy.http import Request
from gpbscraper.items import CompraItem, CompraLineaItem, ProveedorItem
from urlparse import urljoin, urlsplit, urlparse
from datetime import datetime

import django.db.backends.postgresql_psycopg2

class ComprasSpider(BaseSpider):
    name = 'compras'
    allowed_domains = ['moron.gov.ar']

    anio = settings.get('ANIO', datetime.now().year)
    trimestre=settings.get('TRIMESTRE', datetime.now().month // 4 + 1)

    start_urls = ['https://newproxi1.moron.gov.ar/ext/rafam_portal/compras/concluidas.php?rubro=-1&anio=%s&trimestre=%s&crit=P&orden=A&buscar=Buscar' % (anio, trimestre) ]
    #start_urls = ['https://newproxi1.moron.gov.ar/ext/rafam_portal/compras/concluidas.php?rubro=15&anio=%s&trimestre=%s&crit=P&orden=A&buscar=Buscar' % (anio, trimestre) ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        for tr in hxs.select('//div[@id="lasClases"]/table/tr[position() > 1]'):
            cotizacion = tr.select('td[1]/a/text()').extract()[0]
            url_cotizacion = tr.select('td[1]/a/@href').extract()[0]
            url_cotizacion = urljoin(response.url, url_cotizacion)
            url_item = tr.select('td[6]/a/@href').extract()[0]
            url_item = urljoin(response.url, url_item)
            request = Request(url_cotizacion, callback=self.parse_cotizacion)
            request.meta['url_item'] = urljoin(response.url, url_item)
            request.meta['tipo'] = tr.select('td[5]/text()').extract()[0]
            request.meta['cotizacion'] = cotizacion
            yield request

    Destino_RE = re.compile(r"<b>Dependencia solicitante: </b>([^<]*)")

    def parse_cotizacion(self, response):
        destino, = self.Destino_RE.search(response.body).groups()
        url_item = response.request.meta['url_item']
        request = Request(url_item, callback=self.parse_item)
        request.meta['tipo'] = response.request.meta['tipo']
        request.meta['cotizacion'] = response.request.meta['cotizacion']
        request.meta['destino'] = destino
        yield request

    Tooltips_RE = r"Tip\('[^']*', '([^']*)',"

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        for tr in hxs.select('//div[@id="lasClases"]/table/tr[position() > 1]'):
            compra = CompraItem()
            loader = XPathItemLoader(item=compra, selector=tr)
            loader.add_xpath('orden_compra', 'td[1]/text()')
            loader.add_xpath('fecha', 'td[2]/text()')
            loader.add_xpath('importe', 'td[3]/text()')
            loader.add_xpath('proveedor', 'td[4]/text()')
            compra['destino'] = response.request.meta['destino']
            compra['tipo_compra'] = response.request.meta['tipo']
            compra = loader.load_item()

            url = tr.select('td[5]/a/@href').extract()[0]
            url = urljoin(response.url, url)
            request = Request(url, callback=self.parse_details)
            request.meta['compra'] = compra
            
            yield compra
            yield request

        for each in hxs.select('//div[@id="buscador"]/script/text()').re(self.Tooltips_RE):
            proveedor = ProveedorItem()
            proveedor['cuit'] = None
            for line in each.split('<br/>'):
                key, value = line.split('</h2>')
                _, key = key.split('<h2>')
                key = key.strip()
                value = value.strip()
                if   key == u'Razón social:': proveedor['nombre'] = value
                elif key == u'Nombre de fantasía:': pass
                elif key == u'Fecha de alta:': pass
                elif key == u'Tipo de proveedor:': pass
                elif key == u'Cuit:': proveedor['cuit'] = value
                else: raise Exception(u'Unknown field %r' % key)
            if proveedor['cuit']: yield proveedor

    def parse_details(self, response):
        hxs = HtmlXPathSelector(response)
        for tr in hxs.select('//div[@id="lasClases"]/table/tr[position() > 1]'):
            linea = CompraLineaItem()
            loader = XPathItemLoader(item=linea, selector=tr)
            loader.add_xpath('cantidad', 'td[2]/text()')
            loader.add_xpath('unidad_medida', 'td[3]/text()')
            loader.add_xpath('importe', 'td[5]/text()')
            loader.add_xpath('importe_total', 'td[6]/text()')
            loader.add_xpath('detalle', 'td[4]/text()')
            linea['orden_compra'] = response.request.meta['compra']['orden_compra']
            # anio

            yield loader.load_item()

SPIDER = ComprasSpider()
