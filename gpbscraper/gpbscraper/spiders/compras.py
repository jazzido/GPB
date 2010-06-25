import re

from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import XPathItemLoader
from scrapy.spider import BaseSpider
from gpbscraper.items import CompraItem

class ComprasSpider(CrawlSpider):
    name = 'compras'
    allowed_domains = ['bahiablanca.gov.ar']
    start_urls = ['http://www.bahiablanca.gov.ar/compras4/comprasrV2.asp?ejercicio=2010&desde=01/06/2010&hasta=15/06/2010&title=&SUBMIT1=Buscar&page=1']

    rules = (
        Rule(SgmlLinkExtractor(allow=r'/compras4/comprasrV2.asp'), callback='parse_compras', follow=True),
    )

    def parse_compras(self, response):
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
            # TODO -- ir a buscar los 'lineitems' de la compra
            # [u'dcomprV2.asp?wOC=2003&wEjercicio=2010']
            # tengo que hacer urljoin con mi ubicacion actual
            # yield Request(tr.select('td[7]/a/@href').extract()
            yield l.load_item()

SPIDER = ComprasSpider()
