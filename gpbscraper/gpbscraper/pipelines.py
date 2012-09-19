# coding: utf-8
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.xlib.pydispatch import dispatcher
from scrapy.core import signals
from scrapy.core.exceptions import DropItem
from scrapy.core.manager import scrapymanager
from scrapy.http import Request
from scrapy import log
from gpbscraper.items import CompraItem, CompraLineaItem, ProveedorItem 
from gpbscraper.spiders.compras import ComprasSpider
from gpbscraper.spiders.compra_linea import CompraLineasSpider
from gpbweb.core import models

from twisted.internet import defer, threads

from django.db import transaction, connection


class ItemCounterPipeline(object):
    def __init__(self):
        self.proyectos_count = 0
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def process_item(self, spider, item):
        if isinstance(item, CompraItem):
            self.proyectos_count += 1

        return item

    def spider_closed(self, spider):
        print "COMPRAS REGISTRADAS: %s" % self.proyectos_count

class ComprasPersisterPipeline(object):

    def process_item(self, spider, item):
        if isinstance(item, CompraItem):
            self._persistCompraItem(item)

        return item
    
    @transaction.commit_on_success
    def _persistCompraItem(self, compra_item):

        if models.Compra.objects.filter(orden_compra=int(compra_item['orden_compra']), fecha=compra_item['fecha']).exists():
            return

        proveedor, proveedor_created = models.Proveedor.objects.get_or_create(nombre_fantasia=compra_item['proveedor'])
        reparticion, reparticion_created = models.Reparticion.objects.get_or_create_by_canonical_name(compra_item['destino'])

        compra = models.Compra(orden_compra=int(compra_item['orden_compra']),
                               importe=str(compra_item['importe']),
                               fecha=compra_item['fecha'],
                               suministro=compra_item['suministro'],
                               proveedor=proveedor,
                               destino=reparticion)

            
        compra.save()


        # persistir lineas
        for cli in compra_item['compra_linea_items']:
            cli_obj = models.CompraLineaItem(compra=compra,
                                             importe_unitario=str(cli['importe']),
                                             cantidad=cli['cantidad'],
                                             detalle=cli['detalle'],
                                             unidad_medida=cli['unidad_medida'])
            cli_obj.save()

            



class CompraLineasPersisterPipeline(object):
    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
    
    def spider_opened(self, spider):
        for c in models.Compra.objects.filter(compralineaitem=None):
            scrapymanager.engine.crawl(Request('http://www.bahiablanca.gov.ar/compras4/dcomprV2.asp?wOCabc=%s&wEjercicio=%s' % (c.orden_compra, c.fecha.year),
                                               spider.parse),
                                       spider)

    def process_item(self, spider, item):
        @transaction.commit_on_successg
        def persist(item):
            compra = models.Compra.objects.get(fecha__year=item['anio'], orden_compra=int(item['orden_compra']))
            cli_obj = models.CompraLineaItem(compra=compra,
                                             importe_unitario=str(item['importe']),
                                             cantidad=item['cantidad'],
                                             detalle=item['detalle'])
            cli_obj.save()

        if isinstance(item, CompraLineaItem):
            threads.deferToThread(persist, item)

        return item


class ProveedoresPersisterPipeline(object):
    def process_item(self, spider, item):

        @transaction.commit_on_success
        def persist(item):
            if not models.Proveedor.objects.filter(nombre=item['nombre']).exists():
                models.Proveedor(nombre=item['nombre'],
                                 domicilio=item['domicilio'],
                                 cuit=item['cuit'],
                                 localidad=item['localidad']).save()
            else:
                p = models.Proveedor.objects.get(nombre=item['nombre'])
                p.domicilio = item['domicilio']
                p.cuit = item['cuit']
                p.localidad = item['localidad']
                p.save()

        if isinstance(item, ProveedorItem):
            threads.deferToThread(persist, item)
        
        return item
