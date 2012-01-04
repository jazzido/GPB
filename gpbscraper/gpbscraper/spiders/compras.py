import re

from scrapy.conf import settings
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import XPathItemLoader
from scrapy.spider import BaseSpider
from scrapy.http import Request, FormRequest
from scrapy import log
from scrapy.shell import inspect_response

from gpbscraper.items import CompraItem, CompraLineaItem
from urlparse import urljoin, urlsplit, urlparse
from datetime import datetime

import django.db.backends.postgresql_psycopg2

import pickle
import os
import sys

url = 'http://www.bahiablanca.gov.ar/compras/comprasrealizadas.aspx'
NEED_HELP_FILE = '/tmp/need_help'
GOT_HELP_FILE  = '/tmp/got_help'
VIEWSTATE_FILE = '/tmp/viewstate'
MAX_PAGES      = 20000

class ComprasSpider(BaseSpider):
    name = 'compras'
    allowed_domains = ['bahiablanca.gov.ar']
    fecha_desde = settings.get('FECHA_DESDE', datetime(datetime.now().year, datetime.now().month, 1).strftime('%d/%m/%Y'))
    fecha_hasta = settings.get('FECHA_HASTA', datetime.now().strftime('%d/%m/%Y'))
    anio = settings.get('ANIO', settings.get('FECHA_DESDE', datetime(datetime.now().year, datetime.now().month, 1).strftime('%d/%m/%Y')).split('/')[2])

    def help_please(self, *args):
        open(NEED_HELP_FILE,'w').close()
        try: os.unlink(VIEWSTATE_FILE)
        except: pass

        try: os.unlink(GOT_HELP_FILE)
        except: pass
        pass

    def need_help(self, response):
        # we need human help, signal that and flee.
        if ('seguridad erroneo' in response.body) or ('txtCaptcha' in response.body):
           self.help_please()
           return True
        return False

    def formdata(self, viewstate, target, argument):
        data = {
           '__EVENTTARGET':'ctl00$ContentPlaceHolder1$%s' % target,
           '__EVENTARGUMENT':argument,
           '__VIEWSTATEENCRYPTED':'',
           }
        data.update(viewstate)
        return data

    def start_requests(self):

#        if self.fecha_desde.year != self.fecha_hasta.year:
#            raise RuntimeError("Una consulta no puede abarcar mas de un anio")

        self.pages = 0
        try:
           # Try and see if there's already a known __VIEWSTATE
           self.viewstate = pickle.load(open(VIEWSTATE_FILE, 'r'))

           # We don't know the previous state,
           # and the app is very picky. We try to get Page$Last
           # if we are further than 10 pages from the end it'll work
           # if it fails with an error, the flow is wrong, we try Page$First
           # lastPage  = self.formdata(self.viewstate, 'gvOrdenes','Page$253')
           lastPage  = self.formdata(self.viewstate, 'gvOrdenes','Page$Last')
           return  [FormRequest(url, formdata = lastPage, callback = self.parseAPage, errback = self.tryFirst)]
        except:
           try:
              # If there's no stored __VIEWSTATE, try solving the captcha
              formdata = pickle.load(open(GOT_HELP_FILE, 'r'))
              os.unlink(GOT_HELP_FILE)

              txtCaptcha = formdata['txtCaptcha']
              del formdata['txtCaptcha']

              formdata.update({
                  "ctl00$ContentPlaceHolder1$txtCaptcha":txtCaptcha,
                  "__EVENTARGUMENT":"",
                  "__EVENTTARGET":"",
                  "__VIEWSTATEENCRYPTED":"",
                  "ctl00$ContentPlaceHolder1$Button2":"Buscar",
                  "ctl00$ContentPlaceHolder1$meeFechaDesde_ClientState":"",
                  "ctl00$ContentPlaceHolder1$meeFechaHasta_ClientState":"",
                  "ctl00$ContentPlaceHolder1$txtFechaDesde": self.fecha_desde,
                  "ctl00$ContentPlaceHolder1$txtFechaHasta": self.fecha_hasta,
                  "ctl00$ContentPlaceHolder1$ddlEjercicio": self.anio,
                  "ctl00$ContentPlaceHolder1$txtProveedor":"%",
              })
              return [FormRequest(url, formdata = formdata, callback = self.parseFirst, errback = self.help_please)]
           except:
              self.help_please()
           return []

    def tryFirst(self, failure):
        # Page$Last failed, try restart the cycle retrieving Page$First
        formdata = self.formdata(self.viewstate, 'gvOrdenes','Page$First')
        return [FormRequest(url, formdata = formdata, callback = self.parseFirst, errback = self.help_please)]

    def getViewState(self, hxs, save = True):
        viewstate = hxs.select('//input[@name="__VIEWSTATE"]/@value').extract()[0]
        validation = hxs.select('//input[@name="__EVENTVALIDATION"]/@value').extract()[0]
        state = {'__VIEWSTATE':viewstate, '__EVENTVALIDATION':validation}
        if save: pickle.dump(state, open(VIEWSTATE_FILE,'w'))
        return state

    INTERESTING = "javascript:__doPostBack("
    def postBackArgs(self, element):
        url = element.select('@href').extract()
        if not url: return None
        url = url[0].encode('utf-8')
        url = url.split("'")

        if url[0] != self.INTERESTING:
           return None

        target   = url[1].split('$')[2]
        argument = url[3]

        return target, argument

    def parseFirst(self, response):
        # from Page$First we just jump to Page$Last, and start the loop
        if self.need_help(response):
           return

        hxs = HtmlXPathSelector(response)
        viewstate = self.getViewState(hxs)
        
        lastPage  = self.formdata(viewstate, 'gvOrdenes','Page$Last')
        return [FormRequest(url, formdata = lastPage, callback = self.parseAPage, errback = self.help_please)]

    def parseAPage(self, response):
        if self.need_help(response):
           return

        hxs = HtmlXPathSelector(response)
        viewstate = self.getViewState(hxs)
        
        self.pages += 1
        for tr in hxs.select('//table[@id="ctl00_ContentPlaceHolder1_gvOrdenes"]/tr[position() > 1]'):
            detalle = self.postBackArgs(tr.select('td[9]/a'))
            if detalle:
               detalle = self.postBackArgs(tr.select('td[9]/a'))
               i = CompraItem()
               l = XPathItemLoader(item=i, selector=tr)
               l.add_xpath('orden_compra', 'td[1]/text()')
               l.add_xpath('fecha', 'td[2]/text()')
               l.add_xpath('importe', 'td[3]/text()')
               l.add_xpath('proveedor', 'td[4]/text()')
               l.add_xpath('destino', 'td[5]/text()')
               l.add_xpath('suministro', 'td[6]/text()')
               l.add_xpath('anio', 'td[7]/text()')
               l.add_xpath('tipo', 'td[8]/text()')
               compra = l.load_item()
               compra['compra_linea_items'] = []

               detalle  = self.formdata(viewstate, *detalle)
               req = FormRequest(url, formdata = detalle, callback = self.parseDetalle)
               req.meta['compra'] = compra
               req.meta['viewstate'] = viewstate
               yield req

        # Get previous page
        if self.pages < MAX_PAGES:
           prev = None
           for td in hxs.select('//td[@colspan="9"]//td'):
              args = self.postBackArgs(td.select('a'))
              if args:
                 prev = args
              else:
                 prev = self.formdata(viewstate, *prev)
                 req = FormRequest(url, formdata = prev, callback = self.parseAPage)
                 yield req
                      
    def parseDetalle(self, response):
        # Page 253, Orden 2665 has multiple pages
        if self.need_help(response):
           return

        hxs = HtmlXPathSelector(response)

        viewstate = self.getViewState(hxs, save = False)

        orden_compra = response.request.meta['compra']
        hxs = HtmlXPathSelector(response)
        for tr in hxs.select('//table[@id="ctl00_ContentPlaceHolder1_gvDetalle"]/tr[position() > 1]'):
            i = CompraLineaItem()
            l = XPathItemLoader(item=i, selector=tr)
            l.add_xpath('cantidad', 'td[1]/text()')
            l.add_xpath('unidad_medida', 'td[2]/text()')
            l.add_xpath('detalle', 'td[3]/text()')
            l.add_xpath('importe', 'td[4]/text()')
            x = l.load_item()
            
            if 'cantidad' in x:
               orden_compra['compra_linea_items'].append(x)
            foundCurrent = False

        lastPage = True	# when no paging
        foundCurrent = False
        for td in hxs.select('//td[@colspan="4"]//td'):
           lastPage = False	# only commit in the last page
           args = self.postBackArgs(td.select('a'))
           if not args:	# page with no links
              lastPage = True
              foundCurrent = True
           elif foundCurrent:
             args  = self.formdata(viewstate, *args)
             req = FormRequest(url, formdata = args, callback = self.parseDetalle)
             req.meta['compra'] = orden_compra
             yield req
             break

        if lastPage:
           yield orden_compra

SPIDER = ComprasSpider()
