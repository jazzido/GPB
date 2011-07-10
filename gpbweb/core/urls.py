# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from datetime import datetime
from gpbweb.core import feeds

anual_expression   = r'(?P<anio>20\d\d)/'
mensual_expression = r'(?P<anio>20\d\d)/(?P<mes>01|02|03|04|05|06|07|08|09|10|11|12)/'
periodo_expression = r'(?P<start_anio>20\d\d)/(?P<start_mes>01|02|03|04|05|06|07|08|09|10|11|12)/(?P<end_anio>20\d\d)/(?P<end_mes>01|02|03|04|05|06|07|08|09|10|11|12)/'

urlpatterns = patterns('',
                       url(r'^$',
                           'gpbweb.core.views.index',
                           {'start_date': datetime(datetime.now().year, 1, 1),
                            'end_date': datetime(datetime.now().year, 12, 31) },
                           name='index'),

                       url(r'^%s$' % mensual_expression,
                           'gpbweb.core.views.index_mensual',
                           name='index_mensual'),

                       url(r'^%s$' % anual_expression,
                           'gpbweb.core.views.index_anual',
                           name='index_anual'),

                       url(r'^%s$' % periodo_expression,
                           'gpbweb.core.views.index_periodo',
                           name='index_periodo'),

                       url(r'^ordenes-de-compra/$',
                           'gpbweb.core.views.index_ordenes',
                           {'start_date': datetime(datetime.now().year, 1, 1),
                            'end_date': datetime(datetime.now().year, 12, 31) },
                           name='index_ordenes'),
 
                       url(r'^ordenes-de-compra/rss/$',
                           feeds.OrdenesDeCompraFeed(),
                           name="ordenes_rss"
                           ),

                       url(r'^ordenes-de-compra/%s$' % anual_expression,
                           'gpbweb.core.views.index_ordenes_anual',
                           name='index_ordenes_anual'),

                       url(r'^ordenes-de-compra/%s$' % mensual_expression,
                           'gpbweb.core.views.index_ordenes_mensual',
                           name='index_ordenes_mensual'),

                       url(r'^ordenes-de-compra/%s$' % periodo_expression,
                           'gpbweb.core.views.index_ordenes_periodo',
                           name='index_ordenes_periodo'),


                       # --- BEGIN REPARTICIONES ---
                       
                       url(r'^reparticiones/$',
                           'gpbweb.core.views.reparticiones',
                           name='reparticiones'),

                       url(r'^reparticion/(?P<reparticion_slug>[a-z0-9\-]+)/$',
                           'gpbweb.core.views.reparticion',
                           {'start_date': datetime(datetime.now().year, 1, 1),
                            'end_date': datetime(datetime.now().year, 12, 31) },
                           name='reparticion'),

                       url(r'^reparticion/(?P<reparticion_slug>[a-z0-9\-]+)/%s$' % anual_expression,
                           'gpbweb.core.views.reparticion_anual',
                           name='reparticion_anual'),

                       url(r'^reparticion/(?P<reparticion_slug>[a-z0-9\-]+)/%s$' % mensual_expression,
                           'gpbweb.core.views.reparticion_mensual',
                           name='reparticion_mensual'),

                       url(r'^reparticion/(?P<reparticion_slug>[a-z0-9\-]+)/%s$' % periodo_expression,
                           'gpbweb.core.views.reparticion_periodo',
                           name='reparticion_periodo'),

                       url(r'^reparticion/(?P<reparticion_slug>[a-z0-9\-]+)/ordenes-de-compra/$',
                           'gpbweb.core.views.reparticion_ordenes',
                           {'start_date': datetime(datetime.now().year, 1, 1),
                            'end_date': datetime(datetime.now().year, 12, 31) },
                           name='reparticion_ordenes'),

                       url(r'^reparticion/(?P<reparticion_slug>[a-z0-9\-]+)/ordenes-de-compra/rss/$',
                           feeds.ReparticionOrdenesDeCompraFeed(),
                           name="reparticion_ordenes_rss"
                           ),

                       url(r'^reparticion/(?P<reparticion_slug>[a-z0-9\-]+)/ordenes-de-compra/%s$' % anual_expression,
                           'gpbweb.core.views.reparticion_ordenes_anual',
                           name='reparticion_ordenes_anual'),

                       url(r'^reparticion/(?P<reparticion_slug>[a-z0-9\-]+)/ordenes-de-compra/%s$' % mensual_expression,
                           'gpbweb.core.views.reparticion_ordenes_mensual',
                           name='reparticion_ordenes_mensual'),

                       url(r'^reparticion/(?P<reparticion_slug>[a-z0-9\-]+)/ordenes-de-compra/%s$' % periodo_expression,
                           'gpbweb.core.views.reparticion_ordenes_periodo',
                           name='reparticion_ordenes_periodo'),


                       # --- END REPARTICIONES ---

                       # --- BEGIN PROVEEDORES ---

                       url(r'^proveedores/$',
                           'gpbweb.core.views.proveedores',
                           name='proveedores'),

                       url(r'^proveedor/(?P<proveedor_slug>[a-z0-9\-]+)/$',
                           'gpbweb.core.views.proveedor',
                           {'start_date': datetime(datetime.now().year, 1, 1),
                            'end_date': datetime(datetime.now().year, 12, 31) },
                           name='proveedor'),

                       url(r'^proveedor/(?P<proveedor_slug>[a-z0-9\-]+)/%s$' % anual_expression,
                           'gpbweb.core.views.proveedor_anual',
                           name='proveedor_anual'),

                       url(r'^proveedor/(?P<proveedor_slug>[a-z0-9\-]+)/%s$' % mensual_expression,
                           'gpbweb.core.views.proveedor_mensual',
                           name='proveedor_mensual'),

                       url(r'^proveedor/(?P<proveedor_slug>[a-z0-9\-]+)/%s$' % periodo_expression,
                           'gpbweb.core.views.proveedor_periodo',
                           name='proveedor_periodo'),

                       url(r'^proveedor/(?P<proveedor_slug>[a-z0-9\-]+)/ordenes-de-compra/$',
                           'gpbweb.core.views.proveedor_ordenes',
                           {'start_date': datetime(datetime.now().year, 1, 1),
                            'end_date': datetime(datetime.now().year, 12, 31) },
                           name='proveedor_ordenes'),

                       url(r'^proveedor/(?P<proveedor_slug>[a-z0-9\-]+)/ordenes-de-compra/rss/$',
                           feeds.ProveedorOrdenesDeCompraFeed(),
                           name="proveedor_ordenes_rss"
                           ),

                       url(r'^proveedor/(?P<proveedor_slug>[a-z0-9\-]+)/ordenes-de-compra/%s$' % anual_expression,
                           'gpbweb.core.views.proveedor_ordenes_anual',
                           name='proveedor_ordenes_anual'),

                       url(r'^proveedor/(?P<proveedor_slug>[a-z0-9\-]+)/ordenes-de-compra/%s$' % mensual_expression,
                           'gpbweb.core.views.proveedor_ordenes_mensual',
                           name='proveedor_ordenes_mensual'),

                       url(r'^proveedor/(?P<proveedor_slug>[a-z0-9\-]+)/ordenes-de-compra/%s$' % periodo_expression,
                           'gpbweb.core.views.proveedor_ordenes_periodo',
                           name='proveedor_ordenes_periodo'),

                       # --- END PROVEEDORES ---

                       url(r'^orden-de-compra/(?P<numero>[0-9]+)/(?P<anio>[0-9]+)/$',
                           'gpbweb.core.views.orden_de_compra',
                           name='orden_de_compra'),

                       url(r'^orden-de-compra/(?P<numero>[0-9]+)/(?P<anio>[0-9]+)/json$',
                           'gpbweb.core.views.orden_de_compra',
                           { 'format': 'json' },
                           name='orden_de_compra_json'),

                       url(r'^need_help.html$',
                           'gpbweb.core.views.need_help',
                           name='need_help'),


)
