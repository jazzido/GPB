# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from datetime import datetime

anual_expression   = r'(?P<anio>20\d\d)'
mensual_expression = r'(?P<anio>20\d\d)/(?P<mes>01|02|03|04|05|06|07|08|09|10|11|12)'
periodo_expression = r'(?P<start_anio>20\d\d)/(?P<start_mes>01|02|03|04|05|06|07|08|09|10|11|12)/(?P<end_anio>20\d\d)/(?P<end_mes>01|02|03|04|05|06|07|08|09|10|11|12)'

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

                       url(r'^reparticion/(?P<reparticion_slug>[a-z0-9\-]+)$',
                           'gpbweb.core.views.reparticion',
                           {'start_date': datetime(datetime.now().year, datetime.now().month, 1),
                            'end_date': datetime.now() },
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

                       url(r'^proveedor/(?P<proveedor_slug>[a-z0-9\-]+)$',
                           'gpbweb.core.views.proveedor',
                           {'start_date': datetime(datetime.now().year, datetime.now().month, 1),
                            'end_date': datetime.now() },
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



)
