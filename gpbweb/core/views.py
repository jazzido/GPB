from annoying.decorators import render_to
from gpbweb.core import models
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
    gasto_mensual = SortedDict()
    while True:
        c = cursor.fetchone()
        if c is None: break
        gasto_mensual[c[0]] = c[1]

    return gasto_mensual

@render_to('index.html')
def index(request):
    return { 
        'reparticiones': models.Reparticion.objects.por_gastos(),
        'proveedores': models.Proveedor.objects.por_compras(),
        'gasto_mensual_total': models.Compra.objects.total_periodo(),
        'gasto_por_mes': _gasto_por_mes(),
        'fecha_ahora': datetime.now()
        }

def reparticion(request, reparticion_slug):
    reparticion = models.Reparticion.objects.get(slug=reparticion_slug)

    return { 'reparticion': reparticion }


@render_to('proveedor/show.html')
def proveedor(request, proveedor_slug):
    proveedor = models.Proveedor.objects.get(slug=proveedor_slug)

    return { 'proveedor' : proveedor }
