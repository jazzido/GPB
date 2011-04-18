#################################################################################
##### este no se usa mas --- ahora se hace todo junto desde ComprasSpider #######
#################################################################################

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

class CompraLineasSpider(BaseSpider):
    name = 'compra_lineas'

    anio = settings.get('ANIO', datetime.now().year)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        orden_compra, anio = re.search(r'wOCabc=(\d+)&wEjercicio=(\d+)', urlparse(response.url).query).groups()
        for tr in hxs.select('//table[contains(@width, "760")][2]/tr'):
            i = CompraLineaItem()
            l = XPathItemLoader(item=i, selector=tr)
            l.add_xpath('cantidad', 'td[1]/text()')
            l.add_xpath('importe', 'td[2]/text()')
            l.add_xpath('detalle', 'td[3]/text()')
            l.add_value('orden_compra', int(orden_compra))
            l.add_value('anio', int(anio))
            x = l.load_item()
            yield x


SPIDER = CompraLineasSpider()
