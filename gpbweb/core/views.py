# coding: utf-8
from annoying.decorators import render_to
from gpbweb.core import models
from gpbweb.utils import gviz_api
from datetime import datetime
from django.db import connection, transaction
from django.db.models import Sum
from django.utils.datastructures import SortedDict

import calendar

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
    
        

@render_to('index.html')
def index(request, start_date, end_date):

    gasto_por_mes_datatable = gviz_api.DataTable({ "mes": ("date", "Mes"),
                                      "total": ("number", "Gasto") })

    gasto_por_mes_datatable.LoadData(_gasto_por_mes())

    reparticion_gastos_datatable = gviz_api.DataTable({"reparticion": ("string", "Reparticion"),
                                                       "total": ("number", "Gasto")})

    top_reparticiones_por_gastos = models.Reparticion.objects.por_gastos(compra__fecha__gte=start_date,
                                                                         compra__fecha__lte=end_date)

    reparticion_gastos_datatable.LoadData(_reparticion_gastos_data(top_reparticiones_por_gastos))

    return { 
        'reparticiones': top_reparticiones_por_gastos,
        'proveedores': models.Proveedor.objects.por_compras(compra__fecha__gte=start_date, compra__fecha__lte=end_date),
        'gasto_mensual_total': models.Compra.objects.total_periodo(fecha_desde=start_date, fecha_hasta=end_date),
        'gasto_por_mes_datatable_js': gasto_por_mes_datatable.ToJSCode('gasto_por_mes',
                                                                       columns_order=('mes', 'total'),
                                                                       order_by='mes'),
        'reparticion_datatable_js': reparticion_gastos_datatable.ToJSCode('reparticion_gastos',
                                                                         columns_order=('reparticion', 'total'),
                                                                         order_by='reparticion'),
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


@render_to('reparticion/show.html')
def reparticion(request, reparticion_slug, start_date, end_date):
    reparticion = models.Reparticion.objects.get(slug=reparticion_slug)

    return { 'reparticion': reparticion,
             'proveedores': models.Proveedor.objects.por_compras(compra__fecha__gte=start_date, 
                                                                 compra__fecha__lte=end_date, 
                                                                 compra__destino=reparticion),
             'gasto_mensual_total': models.Compra.objects \
                                        .filter(destino=reparticion, 
                                                fecha__gte=start_date, fecha__lte=end_date) \
                                        .aggregate(total=Sum('importe'))['total'],
             'start_date': start_date,
             'end_date': end_date
             }

def reparticion_anual(request, reparticion_slug, anio):
    return reparticion(request, 
                       reparticion_slug,
                       datetime(int(anio), 1, 1), # principio del año
                       datetime(int(anio), 12, 31)) # ultimo dia del año



def reparticion_mensual(request, reparticion_slug, anio, mes):
    return reparticion(request,
                       reparticion_slug,
                       datetime(int(anio), int(mes), 1), # principio del mes
                       datetime(int(anio), int(mes), calendar.monthrange(int(anio), int(mes))[1])) # ultimo dia del mes

def reparticion_periodo(request, reparticion_slug, start_anio, start_mes, end_anio, end_mes):
    return reparticion(request,
                       reparticion_slug,
                       datetime(int(start_anio), int(start_mes), 1), # principio del mes
                       datetime(int(end_anio), int(end_mes), calendar.monthrange(int(end_anio), int(end_mes))[1])) # ultimo dia del mes
                       

@render_to('proveedor/show.html')
def proveedor(request, proveedor_slug, start_date, end_date):
    proveedor = models.Proveedor.objects.get(slug=proveedor_slug)

    return { 'proveedor' : proveedor,
             'clientes': models.Reparticion.objects.por_gastos(compra__fecha__gte=start_date, 
                                                               compra__fecha__lte=end_date,
                                                               compra__proveedor=proveedor),

             'facturacion_mensual_total': models.Compra.objects \
                                             .filter(proveedor=proveedor,
                                                     fecha__gte=start_date, 
                                                     fecha__lte=end_date) \
                                             .aggregate(total=Sum('importe'))['total'] or 0,
             'start_date': start_date,
             'end_date': end_date }

def proveedor_anual(request, proveedor_slug, anio):
    return proveedor(request,
                     proveedor_slug,
                     datetime(int(anio), 1, 1), # principio del año
                     datetime(int(anio), 12, 31)) # ultimo dia del año
                     

def proveedor_mensual(request, proveedor_slug, anio, mes):
    return proveedor(request,
                     proveedor_slug,
                     datetime(int(anio), int(mes), 1), # principio del mes
                     datetime(int(anio), int(mes), calendar.monthrange(int(anio), int(mes))[1])) # ultimo dia del mes

def proveedor_periodo(request, proveedor_slug, start_anio, start_mes, end_anio, end_mes):
    return proveedor(request,
                     proveedor_slug,
                     datetime(int(start_anio), int(start_mes), 1), # principio del mes
                     datetime(int(end_anio), int(end_mes), calendar.monthrange(int(end_anio), int(end_mes))[1])) # ultimo dia del mes
