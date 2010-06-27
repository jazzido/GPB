# coding: utf-8
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.xlib.pydispatch import dispatcher
from scrapy.core import signals
# from scrapy.contrib.exporter.jsonlines import JsonLinesItemExporter
# from scrapy.contrib.exporter import CsvItemExporter, XmlItemExporter, PickleItemExporter
from scrapy.core.exceptions import DropItem
from scrapy import log
from gpbscraper.items import CompraItem, CompraLineaItem
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
    def __init__(self):
        self.compras_line_items = []
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def process_item(self, spider, item):
        if isinstance(item, CompraItem):
            d = threads.deferToThread(self._persistCompraItem, item)
            d.addErrback(log.err, "No pude persistir el item %s" % item)
        elif isinstance(item, CompraLineaItem):
            self.compras_line_items.append(item)

        return item
    
    def _persistCompraItem(self, item):
        def inner(compra_item):
            # fijarse si la orden de compra ya esta persistida. if so, no hacer nada.
            if models.Compra.objects.filter(orden_compra=int(compra_item['orden_compra']), fecha=compra_item['fecha']).exists():
                return

            proveedor, proveedor_created = models.Proveedor.objects.get_or_create(nombre=compra_item['proveedor'])
            reparticion, proveedor_created = models.Reparticion.objects.get_or_create(nombre=compra_item['destino'])
            compra = models.Compra(orden_compra=int(compra_item['orden_compra']),
                                   importe=str(compra_item['importe']),
                                   fecha=compra_item['fecha'],
                                   suministro=compra_item['suministro'],
                                   proveedor=proveedor,
                                   destino=reparticion)
            compra.save()

        transaction.commit_on_success(inner(item))

    @transaction.commit_on_success
    def _persistCompraLineaItem(self, compra_linea_item, compra):
        cli_obj = models.CompraLineaItem(compra=compra,
                                         importe_unitario=str(compra_linea_item['importe']),
                                         cantidad=compra_linea_item['cantidad'],
                                         detalle=compra_linea_item['detalle'])
        cli_obj.save()
            

    def spider_idle(self, spider):
        log.msg("Spider esta idle: consumir los compra_line_items y persistirlos")
        for cli in self.compras_line_items:
            # no vale la pena hacerlo asincronico. Que se bloquee un poco el reactor, no me calienta :)
            # la corrida del spider se hace dentro de un "AÑO" (ejercicio), así que puedo hacer esto:
            compra = models.Compra.objects.get(fecha__year=int(spider.anio), orden_compra=int(cli['orden_compra']))
            self._persistCompraLineaItem(cli, compra)
        self.compra_line_items = []
        

    def spider_closed(self, spider):
        pass
