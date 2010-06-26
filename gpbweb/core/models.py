from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.

class Proveedor(models.Model):
    nombre = models.TextField(_('Nombre'), max_length=256, null=False, blank=True)
    cuit = models.CharField(_('CUIT'), max_length=32, null=True, blank=True)
    domicilio = models.CharField(_('Domicilio'), max_length=128, null=True, blank=True)
    localidad = models.CharField(_('Localidad'), max_length=128, null=True, blank=True)

class Reparticion(models.Model):
    nombre = models.CharField(_('Nombre'), max_length=128, null=False, blank=False)

class Compra(models.Model):
    orden_compra = models.IntegerField(_('Orden de Compra'), null=True, blank=True)
    fecha = models.DateField(_('Fecha'), null=True, blank=True)
    importe = models.DecimalField(_('Importe'), decimal_places=2, max_digits=19)
    suministro = models.CharField(_('Suministro'), max_length=32, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor)
    destino = models.ForeignKey(Reparticion)

class CompraLineaItem(models.Model):
    compra = models.ForeignKey(Compra)
    importe_unitario = models.DecimalField(_('Importe'), decimal_places=2, max_digits=19)
    cantidad = models.CharField(_('Cantidad'), max_length=128, null=True, blank=True)
    detalle = models.TextField(_('Detalle'), null=True, blank=True)


    
