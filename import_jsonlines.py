import re
import sys
import simplejson
import logging
import random
import os
from pprint import pprint

from django.db.models import ObjectDoesNotExist
from django.db.models import Q
from django.db import transaction, connection
import gpbweb.core.models as models 
from datetime import datetime

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


imported_compras = set()

def _import_compra(c):
    proveedor, proveedor_created = models.Proveedor.objects.get_or_create(nombre=c['proveedor'])
    reparticion, reparticion_created = models.Reparticion.objects.get_or_create(nombre=c['destino'])

    if int(c['orden_compra']) in imported_compras: 
      return 

    compra = models.Compra(orden_compra=int(c['orden_compra']),
                           importe=str(c['importe']),
                           fecha=datetime(*map(int, c['fecha'].split('-'))),
                           proveedor=proveedor,
                           destino=reparticion)
    compra.save()

    imported_compras.add(int(c['orden_compra']))

def _import_compralinea(cl):
    try:
        compra = models.Compra.objects.get(orden_compra=int(cl['orden_compra']), fecha__year=os.environ.get('ANIO', datetime.now().year))
        #log.info('getting compra: %s' % compra)
    except ObjectDoesNotExist:
        #log.info('could not get compra with orden_compra = %s' % int(cl['orden_compra']))
        return 
    # ['CompraLineaItem', {'importe_total': 77.0, 'cantidad': '1', 'unidad_medida': 'UNIDAD/ES', 'orden_compra': '1356', 'detalle': 'FILTRO DE ACEITE P/VEHICULO - MARCA FIAT - MODELO DUCATO MAXI CARGO 2.8 P/D- PIEZA PH - 4847 A - MARCA MOTOR FIAT - MODELO MOTOR DUCATO MAXI CARGO 2.8 P/D - TIPO DIESEL - REPUESTO ORIGINAL - FRAM.', 'importe': 77.0}]

    if ('importe' not in cl) or ('cantidad' not in cl): return 

    cant = re.match(r'(\d+)', cl['cantidad'])
    if cant is None: return

    cli = models.CompraLineaItem(compra=compra,
                                 importe_unitario=str(cl['importe']),
                                 cantidad=int(cant.groups()[0]),
                                 detalle=cl['detalle'])

    cli.save()


def import_compras(compras):
    # ['CompraItem', {'proveedor': u'CASTA\xd1O EDUARDO ANIBAL', 'fecha': '2009-08-10', 'destino': u'Secretar\xeda de Salud', 'tipo_compra': 'CDVP', 'orden_compra': '1327', 'observaciones': 'FIAT DUCATO MAXICARGO 2.8 TD-PAT.GYQ 769', 'importe': 350.0}]
    for c in compras:
        transaction.commit_on_success(_import_compra(c))

def import_compra_lineas(compra_lineas):
    for cl in compra_lineas:
        transaction.commit_on_success(_import_compralinea(cl))


def load_lines():
    compras = []
    compra_lineas = []
    for line in sys.stdin:
        r = simplejson.loads(line)
        if r[0] == "CompraItem": compras.append(r[1])
        elif r[0] == "CompraLineaItem": compra_lineas.append(r[1])

    import_compras(compras)
    import_compra_lineas(compra_lineas)


        

    
if __name__ == '__main__':
    load_lines()
