# coding: utf-8
from gpbweb.annoying.decorators import render_to
from gpbweb.core import models
from gpbweb.utils import gviz_api, tagcloud
from datetime import datetime
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db import connection, transaction
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.datastructures import SortedDict
from django.utils import simplejson
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.http import condition
from django.views.decorators.cache import cache_control

# For Colavorative captcha breaking
import urllib2
import random
import pickle
import os

import calendar, csv, hashlib, decimal


PAGE_SIZE = 50
CSV_FIELDNAMES = ['orden_de_compra', 'fecha', 'proveedor', 'destino', 'importe', 'url']

sha1 = lambda m: hashlib.sha1(m).hexdigest()
  

def _gasto_por_mes(additional_where=''):
    cursor = connection.cursor()
    sql = """ SELECT DATE_TRUNC('month', fecha)::date AS mes, SUM(importe) AS importe_total
                               FROM core_compra
                               %(where_clause)s
                               GROUP BY mes
                               ORDER BY mes ASC """ % {'where_clause': additional_where }

    cursor.execute(sql)
    gasto_mensual = []
    while True:
        c = cursor.fetchone()
        if c is None: break
        gasto_mensual.append({'mes': c[0], 'total': float(c[1])})

    return gasto_mensual


def _reparticion_gastos_data(data):
    rv = []
    for r in data[:5]:
        rv.append({'reparticion': r.nombre, 'total': float(r.total_compras)})
    rv.append({'reparticion': 'Resto de las reparticiones', 'total': sum([float(r.total_compras) for r in data[5:]])})
    return rv;
    

def _tagcloud(compra_lineas):
    return tagcloud.make_tagcloud([cli.detalle 
                                   for cli in compra_lineas])

def _get_page(request, param_name='page'):
    try:
        page = int(request.GET.get(param_name, '1'))
    except ValueError:
        page = 1

    return page
        
# @condition(last_modified_func=lambda req, start_date, end_date: models.Compra.objects.filter(fecha__gte=start_date, fecha__lte=end_date).latest('created_at').created_at,
#            etag_func=lambda req, start_date, end_date: sha1('%s:%s' % (req.path, models.Compra.objects.filter(fecha__gte=start_date, fecha__lte=end_date).latest('created_at').created_at)))
# @vary_on_headers('Accept-Encoding')
# @cache_control(must_revalidate=True, max_age=600)
@render_to('index.html')
def index(request, start_date, end_date):
    gasto_por_mes_datatable = gviz_api.DataTable({ "mes": ("date", "Mes"),
                                      "total": ("number", "Gasto") })

    gasto_por_mes_datatable.LoadData(_gasto_por_mes("WHERE core_compra.fecha BETWEEN '%s' AND '%s'" 
                                                    % (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))))

    reparticion_gastos_datatable = gviz_api.DataTable({"reparticion": ("string", "Reparticion"),
                                                       "total": ("number", "Gasto")})

    top_reparticiones_por_gastos = models.Reparticion.objects.por_gastos(compra__fecha__gte=start_date,
                                                                         compra__fecha__lte=end_date)

    reparticion_gastos_datatable.LoadData(_reparticion_gastos_data(top_reparticiones_por_gastos))

    gasto_mensual_total = models.Compra.objects.total_periodo(fecha_desde=start_date, fecha_hasta=end_date)

    

    return { 
        'reparticiones': top_reparticiones_por_gastos,
        'proveedores': models.Proveedor.objects.por_compras(compra__fecha__gte=start_date, compra__fecha__lte=end_date),
        'gasto_mensual_total': gasto_mensual_total,
        'gasto_mensual_promedio': models.Compra.objects.promedio_mensual_periodo(start_date, 
                                                                                 datetime.now() if datetime.now() < end_date else end_date),
        'cantidad_ordenes_de_compra': models.Compra.objects.filter(fecha__gte=start_date, fecha__lte=end_date).count(),
        'ordenes_de_compra': models.Compra.objects.select_related('proveedor', 'destino').filter(fecha__gte=start_date, fecha__lte=end_date).order_by('-fecha')[:100],
        'cantidad_proveedores_unicos': models.Compra.objects.filter(fecha__gte=start_date, fecha__lte=end_date).values('proveedor').distinct().count(),
        'gasto_por_mes_datatable_js': gasto_por_mes_datatable.ToJSCode('gasto_por_mes',
                                                                       columns_order=('mes', 'total'),
                                                                       order_by='mes'),
        'reparticion_datatable_js': reparticion_gastos_datatable.ToJSCode('reparticion_gastos',
                                                                         columns_order=('reparticion', 'total'),
                                                                         order_by='reparticion'),
        'tagcloud': _tagcloud(models.CompraLineaItem.objects.filter(compra__fecha__gte=start_date,  
                                                                    compra__fecha__lte=end_date)),
        'start_date': start_date,
        'end_date': end_date
        }

def index_anual(request, anio):
    return index(request, 
                 datetime(int(anio), 1, 1), # principio del año
                 datetime(int(anio), 12, 31)) # ultimo dia del año

def index_mensual(request, anio, mes):
    return index(request, 
                 datetime(int(anio), int(mes), 1), # principio del mes
                 datetime(int(anio), int(mes), calendar.monthrange(int(anio), int(mes))[1])) # ultimo dia del mes


def index_periodo(request, start_anio, start_mes, end_anio, end_mes):
    return index(request, 
                 datetime(int(start_anio), int(start_mes), 1), # principio del mes
                 datetime(int(end_anio), int(end_mes), calendar.monthrange(int(end_anio), int(end_mes))[1])) # ultimo dia del mes


def ordenes_csv(request, compras, filename):
    """ Renderear un CSV con un QuerySet de ordenes de compra """

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % filename
    
    writer = csv.DictWriter(response, fieldnames=CSV_FIELDNAMES)
    writer.writerow(dict((fn,fn) for fn in CSV_FIELDNAMES))

    # CSV_FIELDNAMES = ['orden_de_compra', 'fecha', 'proveedor', 'destino', 'importe', 'url']

    cur_domain = Site.objects.get_current().domain

    for c in compras:
        writer.writerow({
                'orden_de_compra': c.oc_numero,
                'fecha': c.fecha.strftime('%Y-%m-%d'),
                'proveedor': c.proveedor.nombre.encode('utf-8'),
                'destino': c.destino.nombre.encode('utf-8'),
                'importe': c.importe,
                'url': 'http://%s%s' % (cur_domain, c.get_absolute_url())
                })

    return response


def index_ordenes(request, start_date, end_date):

    if request.GET.get('q') is not None:
        compras = models.Compra.objects.search(' & '.join(request.GET.get('q').split()))
    else:
        compras = models.Compra.objects.select_related('proveedor', 'destino') \
            .filter(fecha__gte=start_date,
                    fecha__lte=end_date) \
                    .order_by('-fecha')
        
    paginator = Paginator(compras, 
                          PAGE_SIZE)

    # Si la pagina esta fuera de rango, mostrar la última
    try:
        ordenes_de_compra = paginator.page(_get_page(request))
    except (EmptyPage, InvalidPage):
        ordenes_de_compra = paginator.page(paginator.num_pages)

    format = request.GET.get('format')

    if format == 'csv':
        return ordenes_csv(request, 
                           compras, 
                           'ordenes-de-compra_%s_%s' % (start_date.strftime('%Y-%m'), end_date.strftime('%Y-%m')))

    return render_to_response('list_ordenes.html',
                              { 'ordenes_de_compra': ordenes_de_compra,
                                'start_date': start_date,
                                'end_date': end_date
                                },
                              context_instance=RequestContext(request))


def index_ordenes_anual(request, anio):
    return index_ordenes(request, 
                         datetime(int(anio), 1, 1), # principio del año
                         datetime(int(anio), 12, 31)) # ultimo dia del año

def index_ordenes_mensual(request, anio, mes):
    return index_ordenes(request, 
                         datetime(int(anio), int(mes), 1), # principio del mes
                         datetime(int(anio), int(mes), calendar.monthrange(int(anio), int(mes))[1])) # ultimo dia del mes

def index_ordenes_periodo(request, start_anio, start_mes, end_anio, end_mes):
    return index_ordenes(request,
                         datetime(int(start_anio), int(start_mes), 1), # principio del mes
                         datetime(int(end_anio), int(end_mes), calendar.monthrange(int(end_anio), int(end_mes))[1])) # ultimo dia del mes



@render_to('reparticion/list.html')
def reparticiones(request):
    return { 'reparticiones': models.Reparticion.objects \
                                     .select_related('compra') \
                                     .annotate(total_compras=Sum('compra__importe')) \
                                     .filter(total_compras__gt=0) \
                                     .order_by('nombre') }


@render_to('reparticion/show.html')
def reparticion(request, reparticion_slug, start_date, end_date):
    
    reparticion = get_object_or_404(models.Reparticion, slug=reparticion_slug)
    facturacion_total_periodo = models.Compra.objects \
        .filter(destino=reparticion, 
                fecha__gte=start_date, fecha__lte=end_date) \
                .aggregate(total=Sum('importe'))['total'] or 0

    return { 'reparticion': reparticion,
             'proveedores': models.Proveedor.objects.por_compras(compra__fecha__gte=start_date, 
                                                                 compra__fecha__lte=end_date, 
                                                                 compra__destino=reparticion),
             'facturacion_total_periodo': facturacion_total_periodo,

             'gasto_mensual_promedio': facturacion_total_periodo / decimal.Decimal(str(((datetime.now() if datetime.now() < end_date else end_date) - start_date).days / 30.0)),

             'ordenes_de_compra': models.Compra.objects \
                                        .select_related('proveedor') \
                                        .filter(fecha__gte=start_date, 
                                                fecha__lte=end_date,
                                                destino=reparticion).order_by('-fecha'),


             'tagcloud': _tagcloud(models.CompraLineaItem.objects \
                                        .filter(compra__fecha__gte=start_date,  
                                                compra__fecha__lte=end_date,
                                                compra__destino=reparticion)),
             'start_date': start_date,
             'end_date': end_date
             }

@render_to('reparticion/list_ordenes.html')
def reparticion_ordenes(request, reparticion_slug, start_date, end_date):
    
    reparticion = get_object_or_404(models.Reparticion, slug=reparticion_slug)

    compras_qs = models.Compra.objects.select_related('proveedor', 'destino') \
                            .filter(fecha__gte=start_date,
                                    fecha__lte=end_date,
                                    destino=reparticion) \
                            .order_by('-fecha')

    # CSV
    format = request.GET.get('format')
    if format == 'csv':
        return ordenes_csv(request,
                           compras_qs,
                           '%s_%s_%s' % (reparticion_slug, start_date.strftime('%Y-%m'), end_date.strftime('%Y-%m')))


    paginator = Paginator(compras_qs, 
                          PAGE_SIZE)

    # Si la pagina esta fuera de rango, mostrar la última
    try:
        ordenes_de_compra = paginator.page(_get_page(request))
    except (EmptyPage, InvalidPage):
        ordenes_de_compra = paginator.page(paginator.num_pages)

    return { 'reparticion': reparticion,
             'ordenes_de_compra': ordenes_de_compra,
             'start_date': start_date,
             'end_date': end_date
             }
                                                               

def reparticion_anual(request, reparticion_slug, anio):
    return reparticion(request, 
                       reparticion_slug,
                       datetime(int(anio), 1, 1), # principio del año
                       datetime(int(anio), 12, 31)) # ultimo dia del año


def reparticion_ordenes_anual(request, reparticion_slug, anio):
    return reparticion_ordenes(request, 
                               reparticion_slug, 
                               datetime(int(anio), 1, 1), # principio del año
                               datetime(int(anio), 12, 31)) # ultimo dia del año

def reparticion_mensual(request, reparticion_slug, anio, mes):
    return reparticion(request,
                       reparticion_slug,
                       datetime(int(anio), int(mes), 1), # principio del mes
                       datetime(int(anio), int(mes), calendar.monthrange(int(anio), int(mes))[1])) # ultimo dia del mes

def reparticion_ordenes_mensual(request, reparticion_slug, anio, mes):
    return reparticion_ordenes(request,
                               reparticion_slug,
                               datetime(int(anio), int(mes), 1), # principio del mes
                               datetime(int(anio), int(mes), calendar.monthrange(int(anio), int(mes))[1])) # ultimo dia del mes
                       
def reparticion_periodo(request, reparticion_slug, start_anio, start_mes, end_anio, end_mes):
    return reparticion(request,
                       reparticion_slug,
                       datetime(int(start_anio), int(start_mes), 1), # principio del mes
                       datetime(int(end_anio), int(end_mes), calendar.monthrange(int(end_anio), int(end_mes))[1])) # ultimo dia del mes


def reparticion_ordenes_periodo(request, reparticion_slug, start_anio, start_mes, end_anio, end_mes):
    return reparticion_ordenes(request,
                               reparticion_slug,
                               datetime(int(start_anio), int(start_mes), 1), # principio del mes
                               datetime(int(end_anio), int(end_mes), calendar.monthrange(int(end_anio), int(end_mes))[1])) # ultimo dia del mes
    
                       
@render_to('proveedor/list.html')
def proveedores(request):
    return { 'proveedores': models.Proveedor.objects \
                                     .select_related('compra') \
                                     .annotate(total_compras=Sum('compra__importe')) \
                                     .filter(total_compras__gt=0) \
                                     .order_by('nombre') }

@render_to('proveedor/show.html')
def proveedor(request, proveedor_slug, start_date, end_date):
    proveedor = get_object_or_404(models.Proveedor, slug=proveedor_slug)

    ordenes_de_compra = models.Compra.objects.filter(fecha__gte=start_date, 
                                                     fecha__lte=end_date,
                                                     proveedor=proveedor).order_by('-fecha')

    facturacion_total_periodo = ordenes_de_compra.aggregate(total=Sum('importe'))['total'] or 0

    # print facturacion_total_periodo / decimal.Decimal(str(((datetime.now() if datetime.now() < end_date else end_date) - start_date).days / 30.0))

    return { 'proveedor' : proveedor,
             'clientes': models.Reparticion.objects.por_gastos(compra__fecha__gte=start_date, 
                                                               compra__fecha__lte=end_date,
                                                               compra__proveedor=proveedor),

             'facturacion_total_periodo': facturacion_total_periodo,
             'ordenes_de_compra': ordenes_de_compra,
             'gasto_mensual_promedio': facturacion_total_periodo / decimal.Decimal(str(((datetime.now() if datetime.now() < end_date else end_date) - start_date).days / 30.0)),

             'tagcloud': _tagcloud(models.CompraLineaItem.objects.filter(compra__fecha__gte=start_date,
                                                                         compra__fecha__lte=end_date,
                                                                         compra__proveedor=proveedor)),

             'start_date': start_date,
             'end_date': end_date }


@render_to('proveedor/list_ordenes.html')
def proveedor_ordenes(request, proveedor_slug, start_date, end_date):
    proveedor = get_object_or_404(models.Proveedor, slug=proveedor_slug)


    compras_qs = models.Compra.objects.select_related('destino', 'proveedor') \
                            .filter(fecha__gte=start_date,
                                    fecha__lte=end_date,
                                    proveedor=proveedor) \
                            .order_by('-fecha')
    paginator = Paginator(compras_qs,
                          PAGE_SIZE)


    # CSV
    format = request.GET.get('format')
    if format == 'csv':
        return ordenes_csv(request,
                           compras_qs,
                           '%s_%s_%s' % (proveedor_slug, start_date.strftime('%Y-%m'), end_date.strftime('%Y-%m')))


    # Si la pagina esta fuera de rango, mostrar la última
    try:
        ordenes_de_compra = paginator.page(_get_page(request))
    except (EmptyPage, InvalidPage):
        ordenes_de_compra = paginator.page(paginator.num_pages)

    return { 'proveedor': proveedor,
             'ordenes_de_compra': ordenes_de_compra,
             'start_date': start_date,
             'end_date': end_date
             }


def proveedor_anual(request, proveedor_slug, anio):
    return proveedor(request,
                     proveedor_slug,
                     datetime(int(anio), 1, 1), # principio del año
                     datetime(int(anio), 12, 31)) # ultimo dia del año
                     
def proveedor_ordenes_anual(request, proveedor_slug, anio):
    return proveedor_ordenes(request,
                             proveedor_slug,
                             datetime(int(anio), 1, 1), # principio del año
                             datetime(int(anio), 12, 31)) # ultimo dia del año


def proveedor_mensual(request, proveedor_slug, anio, mes):
    return proveedor(request,
                     proveedor_slug,
                     datetime(int(anio), int(mes), 1), # principio del mes
                     datetime(int(anio), int(mes), calendar.monthrange(int(anio), int(mes))[1])) # ultimo dia del mes

def proveedor_ordenes_mensual(request, proveedor_slug, anio, mes):
    return proveedor_ordenes(request,
                             proveedor_slug,
                             datetime(int(anio), int(mes), 1), # principio del mes
                             datetime(int(anio), int(mes), calendar.monthrange(int(anio), int(mes))[1])) # ultimo dia del mes


def proveedor_periodo(request, proveedor_slug, start_anio, start_mes, end_anio, end_mes):
    return proveedor(request,
                     proveedor_slug,
                     datetime(int(start_anio), int(start_mes), 1), # principio del mes
                     datetime(int(end_anio), int(end_mes), calendar.monthrange(int(end_anio), int(end_mes))[1])) # ultimo dia del mes

def proveedor_ordenes_periodo(request, proveedor_slug, start_anio, start_mes, end_anio, end_mes):
    return proveedor_ordenes(request,
                             proveedor_slug,
                             datetime(int(start_anio), int(start_mes), 1), # principio del mes
                             datetime(int(end_anio), int(end_mes), calendar.monthrange(int(end_anio), int(end_mes))[1])) # ultimo dia del mes


def orden_de_compra(request, numero, anio, format='html'):
    orden = get_object_or_404(models.Compra, orden_compra=int(numero), fecha__year=int(anio))
    if format == 'html':
        return render_to_response('orden_de_compra.html',
                                  { 'orden': orden },
                                  context_instance=RequestContext(request))
    elif format == 'json':
        response = HttpResponse(content_type = 'application/javascript')

        obj = { 'href': orden.get_absolute_url(),
                'numero': orden.oc_numero,
                'fecha': orden.fecha.strftime('%Y-%m-%d'),
                'importe': str(orden.importe),
                'proveedor': { 'nombre': orden.proveedor.nombre,
                               'href': orden.proveedor.get_absolute_url() },
                'destino': { 'nombre': orden.destino.nombre,
                             'href': orden.destino.get_absolute_url() },
                'lineas': [ { 'cantidad': cli.cantidad,
                              'importe_unitario': str(cli.importe_unitario),
                              'detalle': cli.detalle } for cli in orden.compralineaitem_set.all()]
                }

        simplejson.dump(obj, response)

        return response

    else:
        return HttpResponseBadRequest()
              
                             
@render_to('need_help.html')
def need_help(request, format='html'):
    NEED_HELP_FILE = '/tmp/need_help'
    GOT_HELP_FILE  = '/tmp/got_help'
    base = 'http://www.bahiablanca.gov.ar/compras/%s'
    captchaSource = base % 'comprasrealizadas.aspx'

    msg = 'no message'
    if request.POST:
       show = True
       msg = 'Gracias! sos el colaborador numero %d' % random.randint(1,100000000000)
       viewstate  = request.POST['__VIEWSTATE']
       validation = request.POST['__EVENTVALIDATION']
       txtCaptcha = request.POST['txtCaptcha'].upper()
       save = int(request.POST['save'])

       got_help = {
          '__VIEWSTATE' : viewstate,
          '__EVENTVALIDATION' : validation,
          'txtCaptcha'  : txtCaptcha,
       }
       if save:
          pickle.dump(got_help,open(GOT_HELP_FILE,'w'))
          try:
             os.unlink(NEED_HELP_FILE)
          except:
             pass
    else:
       msg = ''
       # GET
       show = not random.randint(0,20)
       save = 0
       try:
          open(NEED_HELP_FILE,'r').close()
          show = save = 1
       except:
          # file doesn't exist, we don't need help

          # Show it anyway 1 every 20 users so we renew the captcha
          if not show: return vars()

       txtCaptcha = 'CaptchaImage.axd?guid='
       viewstate  = 'id="__VIEWSTATE'
       validation = 'id="__EVENTVALIDATION'
       
       r = urllib2.urlopen(captchaSource).read()
       def extract(html, pattern1, pattern2 = ''):
           pattern    = html.index(pattern1)
           if pattern2:
              pattern = html.index(pattern2, pattern)

           patternEnd = html.index('"', pattern+len(pattern2))
           pattern    = html[pattern+len(pattern2):patternEnd]
           return pattern

       try:
          txtCaptcha = base % extract(r, txtCaptcha)
          viewstate  = extract(r, viewstate, 'value="')
          validation = extract(r, validation, 'value="')
       except:
          msg = 'La pagina de la municipalidad cambio, por favor comuniquese con manu'
    return vars()

