# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from datetime import datetime

mensual_expression = r'(?P<anio>20\d\d)/(?P<mes>01|02|03|04|05|06|07|08|09|10|11|12)'
periodo_expression = r'(?P<start_anio>20\d\d)/(?P<start_mes>01|02|03|04|05|06|07|08|09|10|11|12)/(?P<end_anio>20\d\d)/(?P<end_mes>01|02|03|04|05|06|07|08|09|10|11|12)'

urlpatterns = patterns('',
                       url(r'^$',
                           'gpbweb.core.views.index',
                           {'start_date': datetime(datetime.now().year, datetime.now().month, 1),
                            'end_date': datetime.now() },
                           name='index'),
                       url(r'^%s$' % mensual_expression,
                           'gpbweb.core.views.index_mensual',
                           name='index_mensual'),

                       url(r'^reparticion/(?P<reparticion_slug>[a-z0-9\-]+)$',
                           'gpbweb.core.views.reparticion',
                           {'start_date': datetime(datetime.now().year, datetime.now().month, 1),
                            'end_date': datetime.now() },
                           name='reparticion'),

                       url(r'^reparticion/(?P<reparticion_slug>[a-z0-9\-]+)/%s$' % mensual_expression,
                           'gpbweb.core.views.reparticion_mensual',
                           name='reparticion_mensual'),


                       url(r'^proveedor/(?P<proveedor_slug>.+)$',
                           'gpbweb.core.views.proveedor',
                           name='proveedor')

)
