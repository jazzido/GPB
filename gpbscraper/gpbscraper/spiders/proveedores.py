import re

from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from gpbscraper.items import ProveedorItem

class ProveedoresSpider(CrawlSpider):
    name = 'proveedores'
    allowed_domains = ['bahiablanca.gov.ar']
    start_urls = ['http://www.bahiablanca.gov.ar/compras4/proveedV2.asp']

    extractor = SgmlLinkExtractor(allow=r'proveedV2')

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for tr in hxs.select('//div[@id="miListView"]/table/tr'):
            i = ProveedorItem()
            l = XPathItemLoader(item=i, selector=tr)
            l.add_xpath('nombre', 'td[1]/text()')
            l.add_xpath('domicilio', 'td[2]/text()')
            l.add_xpath('cuit', 'td[3]/text()')
            l.add_xpath('localidad', 'td[4]/text()')

            yield l.load_item()

        for l in self.extractor.extract_links(response):
            yield Request(l.url, callback=self.parse)


SPIDER = ProveedoresSpider()
