# coding: utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db import fields

from datetime import datetime
# Create your models here.

class ProveedorManager(models.Manager):

    def por_compras(self, **filter_args):

        filter_args['compra__fecha__gte'] = filter_args.get('compra__fecha__gte', datetime(datetime.now().year, datetime.now().month, 1))
        filter_args['compra__fecha__lte'] = filter_args.get('compra__fecha__lte', datetime.now())

        return self.select_related('compra_set') \
            .filter(**filter_args) \
            .annotate(total_compras=models.Sum('compra__importe')) \
            .order_by('-total_compras')

class Proveedor(models.Model):

    objects = ProveedorManager()

    nombre = models.TextField(_('Nombre'), max_length=256, null=False, blank=True, unique=True)
    cuit = models.CharField(_('CUIT'), max_length=32, null=True, blank=True)
    domicilio = models.CharField(_('Domicilio'), max_length=128, null=True, blank=True)
    localidad = models.CharField(_('Localidad'), max_length=128, null=True, blank=True)
    slug = fields.AutoSlugField(populate_from='nombre', overwrite=True)

    def __unicode__(self):
        return self.nombre

    @models.permalink
    def get_absolute_url(self):
        return ('gpbweb.core.views.proveedor', (),
                {'proveedor_slug': self.slug})


class ReparticionManager(models.Manager):
    def por_gastos(self, **filter_args):
        """ Lista de Reparticion ordenadas por la que mas gastos produjo en un período """

        filter_args['compra__fecha__gte'] = filter_args.get('compra__fecha__gte', datetime(datetime.now().year, datetime.now().month, 1))
        filter_args['compra__fecha__lte'] = filter_args.get('compra__fecha__lte', datetime.now())

        return self.select_related('compra_set') \
            .filter(**filter_args) \
            .annotate(total_compras=models.Sum('compra__importe')) \
            .order_by('-total_compras')

class Reparticion(models.Model):

    objects = ReparticionManager()

    nombre = models.CharField(_('Nombre'), max_length=128, null=False, blank=False, unique=True)
    slug = fields.AutoSlugField(populate_from='nombre', overwrite=True)

    def __unicode__(self):
        return self.nombre

    @models.permalink
    def get_absolute_url(self):
        return ('gpbweb.core.views.reparticion', (),
                {'reparticion_slug': self.slug})


class CompraManager(models.Manager):
    def total_periodo(self, fecha_desde=datetime(datetime.now().year, datetime.now().month, 1), fecha_hasta=datetime.now()):
        return self.filter(fecha__gte=fecha_desde, fecha__lte=fecha_hasta).aggregate(total=models.Sum('importe'))['total'] or 0

class Compra(models.Model):

    objects = CompraManager()

    orden_compra = models.IntegerField(_('Orden de Compra'), null=True, blank=True)
    fecha = models.DateField(_('Fecha'), null=True, blank=True)
    importe = models.DecimalField(_('Importe'), decimal_places=2, max_digits=19)
    suministro = models.CharField(_('Suministro'), max_length=32, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor)
    destino = models.ForeignKey(Reparticion)

    def oc_numero(self):
        return "%s/%s" % (self.orden_compra, self.fecha.strftime("%Y"))

    def __unicode__(self):
        return "%s compra a %s por $%s" % (self.destino, self.proveedor, self.importe)

class CompraLineaItem(models.Model):
    compra = models.ForeignKey(Compra)
    importe_unitario = models.DecimalField(_('Importe'), decimal_places=2, max_digits=19)
    cantidad = models.CharField(_('Cantidad'), max_length=128, null=True, blank=True)
    detalle = models.TextField(_('Detalle'), null=True, blank=True)
