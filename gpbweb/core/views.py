# coding: utf-8
from gpbweb.annoying.decorators import render_to
from gpbweb.core import models
from gpbweb.utils import gviz_api, tagcloud
from datetime import datetime
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db import connection, transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils.datastructures import SortedDict

import calendar

PAGE_SIZE = 50

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
    rv.append({'reparticion': 'Otras Reparticiones', 'total': sum([float(r.total_compras) for r in data[5:]])})
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


    return { 
        'reparticiones': top_reparticiones_por_gastos,
        'proveedores': models.Proveedor.objects.por_compras(compra__fecha__gte=start_date, compra__fecha__lte=end_date),
        'gasto_mensual_total': models.Compra.objects.total_periodo(fecha_desde=start_date, fecha_hasta=end_date),
        'ordenes_de_compra': models.Compra.objects.filter(fecha__gte=start_date, fecha__lte=end_date).order_by('-fecha')[:100],
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



@render_to('list_ordenes.html')
def index_ordenes(request, start_date, end_date):

    paginator = Paginator(models.Compra.objects.select_related('proveedor') \
                            .filter(fecha__gte=start_date,
                                    fecha__lte=end_date) \
                            .order_by('-fecha'), 
                          PAGE_SIZE)

    # Si la pagina esta fuera de rango, mostrar la última
    try:
        ordenes_de_compra = paginator.page(_get_page(request))
    except (EmptyPage, InvalidPage):
        ordenes_de_compra = paginator.page(paginator.num_pages)

    return { 'ordenes_de_compra': ordenes_de_compra,
             'start_date': start_date,
             'end_date': end_date
             }

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

    return { 'reparticion': reparticion,
             'proveedores': models.Proveedor.objects.por_compras(compra__fecha__gte=start_date, 
                                                                 compra__fecha__lte=end_date, 
                                                                 compra__destino=reparticion),
             'gasto_mensual_total': models.Compra.objects \
                                        .filter(destino=reparticion, 
                                                fecha__gte=start_date, fecha__lte=end_date) \
                                        .aggregate(total=Sum('importe'))['total'] or 0,

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

    paginator = Paginator(models.Compra.objects.select_related('proveedor') \
                            .filter(fecha__gte=start_date,
                                    fecha__lte=end_date,
                                    destino=reparticion) \
                            .order_by('-fecha'), 
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

    return { 'proveedor' : proveedor,
             'clientes': models.Reparticion.objects.por_gastos(compra__fecha__gte=start_date, 
                                                               compra__fecha__lte=end_date,
                                                               compra__proveedor=proveedor),

             'facturacion_mensual_total': models.Compra.objects \
                                             .filter(proveedor=proveedor,
                                                     fecha__gte=start_date, 
                                                     fecha__lte=end_date) \
                                             .aggregate(total=Sum('importe'))['total'] or 0,

             'ordenes_de_compra': models.Compra.objects.filter(fecha__gte=start_date, 
                                                               fecha__lte=end_date,
                                                               proveedor=proveedor).order_by('-fecha'),

             'tagcloud': _tagcloud(models.CompraLineaItem.objects.filter(compra__fecha__gte=start_date,  
                                                                         compra__fecha__lte=end_date,
                                                                         compra__proveedor=proveedor)),

             'start_date': start_date,
             'end_date': end_date }


@render_to('proveedor/list_ordenes.html')
def proveedor_ordenes(request, proveedor_slug, start_date, end_date):
    proveedor = get_object_or_404(models.Proveedor, slug=proveedor_slug)

    paginator = Paginator(models.Compra.objects.select_related('destino') \
                            .filter(fecha__gte=start_date,
                                    fecha__lte=end_date,
                                    proveedor=proveedor) \
                            .order_by('-fecha'), 
                          PAGE_SIZE)

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


@render_to('orden_de_compra.html')
def orden_de_compra(request, numero, anio):
    orden = get_object_or_404(models.Compra, orden_compra=int(numero), fecha__year=int(anio))
    return { 'orden': orden }
