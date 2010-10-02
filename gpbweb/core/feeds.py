# coding: utf-8

from gpbweb.core import models
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from datetime import datetime

class OrdenesDeCompraFeed(Feed):

    description_template = "feeds/orden_de_compra_description.html"
    link = "/"

    def title(self):
        return "Gasto Público Marplatense: Últimas órdenes de compra"

    def description(self):
        description = "Últimas órdenes de compra publicadas por la Municipalidad de Mar del Plata"

    def _items(self):
        return models.Compra.objects.select_related('destino', 'proveedor') \
            .order_by('-fecha').all()

    def items(self):
        return self._items()[:100]

    def item_title(self, item):
        return "OC %s: Adjudicada a %s con destino %s. Importe $ %s" % (item.oc_numero,
                                                                        item.proveedor,
                                                                        item.destino,
                                                                        item.importe)

    def item_pubdate(self, item):
        return datetime(item.fecha.year, item.fecha.month, item.fecha.day)


class ProveedorOrdenesDeCompraFeed(OrdenesDeCompraFeed):

    def title(self, obj):
        return OrdenesDeCompraFeed.title(self) + ' adjudicadas a %s' % obj

    description = title

    def get_object(self, request, proveedor_slug):
        return get_object_or_404(models.Proveedor, slug=proveedor_slug)

    def items(self, obj):
        return self._items().filter(proveedor=obj)[:100]

class ReparticionOrdenesDeCompraFeed(OrdenesDeCompraFeed):

    def title(self, obj):
        return OrdenesDeCompraFeed.title(self) + ' con destino %s' % obj

    description = title

    def get_object(self, request, reparticion_slug):
        return get_object_or_404(models.Reparticion, slug=reparticion_slug)

    def items(self, obj):
        return self._items().filter(destino=obj)[:100]

