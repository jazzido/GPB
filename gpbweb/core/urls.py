# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       url(r'^$',
                           'gpbweb.core.views.index',
                           name='index'),
                       url(r'^reparticion/(?P<reparticion_slug>.+)$',
                           'gpbweb.core.views.reparticion',
                           name='reparticion'),
                       url(r'^proveedor/(?P<proveedor_slug>.+)$',
                           'gpbweb.core.views.proveedor',
                           name='proveedor')

)
