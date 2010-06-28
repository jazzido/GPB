from annoying.decorators import render_to
from gpbweb.core import models
from gpbweb.utils import gviz_api
from datetime import datetime
from django.db import connection, transaction
from django.utils.datastructures import SortedDict


def _gasto_por_mes():
    cursor = connection.cursor()
    sql = """ SELECT DATE_TRUNC('month', fecha)::date AS mes, SUM(importe) AS importe_total
                               FROM core_compra
                               GROUP BY mes
                               ORDER BY mes ASC """
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
def index(request):
    
    gasto_por_mes_datatable = gviz_api.DataTable({ "mes": ("date", "Mes"),
                                      "total": ("number", "Gasto") })

    gasto_por_mes_datatable.LoadData(_gasto_por_mes())

    reparticion_gastos_datatable = gviz_api.DataTable({"reparticion": ("string", "Reparticion"),
                                                       "total": ("number", "Gasto")})

    reparticion_gastos_datatable.LoadData(_reparticion_gastos_data(models.Reparticion.objects.por_gastos()))

    return { 
        'reparticiones': models.Reparticion.objects.por_gastos(),
        'proveedores': models.Proveedor.objects.por_compras(),
        'gasto_mensual_total': models.Compra.objects.total_periodo(),
        'gasto_por_mes_datatable_js': gasto_por_mes_datatable.ToJSCode('gasto_por_mes',
                                                                       columns_order=('mes', 'total'),
                                                                       order_by='mes'),
        'reparticion_datatable_js': reparticion_gastos_datatable.ToJSCode('reparticion_gastos',
                                                                         columns_order=('reparticion', 'total'),
                                                                         order_by='reparticion'),
        'fecha_ahora': datetime.now(),
        }

def reparticion(request, reparticion_slug):
    reparticion = models.Reparticion.objects.get(slug=reparticion_slug)

    return { 'reparticion': reparticion }


@render_to('proveedor/show.html')
def proveedor(request, proveedor_slug):
    proveedor = models.Proveedor.objects.get(slug=proveedor_slug)

    return { 'proveedor' : proveedor }
