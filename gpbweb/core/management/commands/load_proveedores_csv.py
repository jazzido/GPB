import csv, sys

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import Proveedor


class Command(BaseCommand):
    args = '<csv_file>'
    help = 'Carga proveedores de un CSV'

    def handle(self, *args, **options):
        csv_file = csv.reader(open(args[0], 'r'))
        csv_lines = list(csv_file)[1:] # saco el header
        
        # remove cuit dupes
        self._doit(csv_lines)

    @transaction.commit_on_success
    def _doit(self, lines):
        for line in lines:
            nombre_fantasia, razon_social, cuit = map(lambda x: x.decode('utf-8'), line)

            print >>sys.stderr, ("Proveedor: [%s, %s, %s]" % (nombre_fantasia, razon_social, cuit))
            
            # busco por cuit
            try:
                proveedor = Proveedor.objects.get(cuit=cuit)
                proveedor.nombre_fantasia = nombre_fantasia
                proveedor.nombre = razon_social
                proveedor.save()
                print >>sys.stderr, "   Encontre el CUIT."
                continue
            except Proveedor.DoesNotExist:
                pass # XXX aca que hago?

            # busco por razon social
            try:
                proveedor = Proveedor.objects.get(nombre=razon_social)
                proveedor.nombre_fantasia = nombre_fantasia
                proveedor.cuit = cuit
                proveedor.save()
                print >>sys.stderr, "   Encontre por razon social"
                continue
            except Proveedor.DoesNotExist:
                #print >>sys.stderr, ("   No existe registro para este proveedor: [%s, %s, %s]" % (nombre_fantasia, razon_social, cuit))
                pass

            # no esta, deberia crearlo
            proveedor = Proveedor(nombre=razon_social, nombre_fantasia=nombre_fantasia, cuit=cuit)
            proveedor.save()
            print >>sys.stderr, "  Nuevo proveedor creado"
            print >>sys.stderr

            
        

