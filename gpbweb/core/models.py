# coding: utf-8

import decimal
from datetime import datetime

from django.db import models, connection, transaction
from django.utils.translation import ugettext_lazy as _

from django_extensions.db import fields

from gpbweb.postgres_fts import models as fts_models

from south.modelsinspector import add_ignored_fields

add_ignored_fields(["^gpbweb\.postgres_fts\.models\.VectorField",])


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

    created_at = fields.CreationDateTimeField()

    def __unicode__(self):
        return self.nombre

    @models.permalink
    def get_absolute_url(self):
        return ('gpbweb.core.views.proveedor', (),
                {'proveedor_slug': self.slug})


class ReparticionSinonimo(models.Model):
    nombre = models.TextField(_('Nombre'), max_length=128, null=False, blank=False, unique=True)
    canonico = models.ForeignKey('Reparticion', related_name='sinonimos')

    class Meta:
        unique_together = (('nombre', 'canonico',))


class ReparticionManager(models.Manager):
    def por_gastos(self, **filter_args):
        """ Lista de Reparticion ordenadas por la que mas gastos produjo en un período """

        filter_args['compra__fecha__gte'] = filter_args.get('compra__fecha__gte', datetime(datetime.now().year, datetime.now().month, 1))
        filter_args['compra__fecha__lte'] = filter_args.get('compra__fecha__lte', datetime.now())

        return self.select_related('compra_set') \
            .filter(**filter_args) \
            .annotate(total_compras=models.Sum('compra__importe')) \
            .order_by('-total_compras')

    def get_or_create_by_canonical_name(self, nombre):
        """ Obtiene una `Reparticion` por su nombre canónico (ie. usando `ReparticionSinonimo`) """
        try:
            # imitar el retorno de get_or_create
            return (ReparticionSinonimo.objects.get(nombre=nombre).canonico, False)
        except models.ObjectDoesNotExist:
            return self.get_or_create(nombre=nombre)

class Reparticion(models.Model):

    objects = ReparticionManager()

    nombre = models.CharField(_('Nombre'), max_length=128, null=False, blank=False, unique=True)
    slug = fields.AutoSlugField(populate_from='nombre', overwrite=True)

    created_at = fields.CreationDateTimeField()

    def __unicode__(self):
        return self.nombre

    @models.permalink
    def get_absolute_url(self):
        return ('gpbweb.core.views.reparticion', (),
                {'reparticion_slug': self.slug})


class CompraManager(models.Manager):
    def total_periodo(self, fecha_desde=datetime(datetime.now().year, datetime.now().month, 1), fecha_hasta=datetime.now()):
        return self.filter(fecha__gte=fecha_desde, fecha__lte=fecha_hasta).aggregate(total=models.Sum('importe'))['total'] or 0

    # es medio hacky, pero es lo que hay
    # idea encontrada aca: http://www.caktusgroup.com/blog/2009/09/28/custom-joins-with-djangos-queryjoin/
    def search(self, query):
        c = self.extra(select={ 'rank': 'ts_rank_cd(core_compralineaitem.search_index, to_tsquery(\'spanish\', E\'%s\'), %d)' % (query, 32), 
                                'highlight_proveedor': 'ts_headline(\'spanish\', core_proveedor.nombre, to_tsquery(\'spanish\', E\'%s\'), \'StartSel=<em>, StopSel=</em>\')' % (query),
                                'highlight_reparticion': 'ts_headline(\'spanish\', core_reparticion.nombre, to_tsquery(\'spanish\', E\'%s\'), \'StartSel=<em>, StopSel=</em>\')' % (query)},
                       where=["core_compralineaitem.search_index @@ to_tsquery('spanish', %s)"
                              " OR core_proveedor.search_index @@ to_tsquery('spanish', %s)"
                              " OR core_reparticion.search_index @@ to_tsquery('spanish', %s)"],
                       params=[query, query, query]).select_related('proveedor', 'destino')

        c.select_related('proveedor', 'destino')

        c.query.join((None, Compra._meta.db_table, None, None,))
        c.query.join((Compra._meta.db_table,  # core_compra
                      CompraLineaItem._meta.db_table, # core_compralineaitem, 
                      'id', 
                      'compra_id'), 
                     promote=True)
        c.query.join((Compra._meta.db_table,
                      Proveedor._meta.db_table,
                      'proveedor_id',
                      'id',),
                     promote=True)
        c.query.join((Compra._meta.db_table,
                      Reparticion._meta.db_table,
                      'destino_id',
                      'id',),
                     promote=True)

        return c.distinct().order_by('-fecha', '-rank')

    def promedio_mensual_periodo(self, fecha_desde, fecha_hasta):
        """ Gasto promedio cada 30 dias """

        t = self.total_periodo(fecha_desde, fecha_hasta)
        return t / decimal.Decimal(str((fecha_hasta - fecha_desde).days / 30.0))


class Compra(models.Model):

    objects = CompraManager()

    orden_compra = models.IntegerField(_('Orden de Compra'), null=True, blank=True)
    fecha = models.DateField(_('Fecha'), null=True, blank=True)
    importe = models.DecimalField(_('Importe'), decimal_places=2, max_digits=19)
    suministro = models.CharField(_('Suministro'), max_length=32, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor)
    destino = models.ForeignKey(Reparticion)

    created_at = fields.CreationDateTimeField()

    def _oc_numero(self):
        return "%s/%s" % (self.orden_compra, self.fecha.strftime("%Y"))
    oc_numero = property(_oc_numero)


    def __unicode__(self):
        return "%s compra a %s por $%s" % (self.destino, self.proveedor, self.importe)

    @models.permalink
    def get_absolute_url(self):
        return ('orden_de_compra', (),
                {'numero': self.orden_compra,
                 'anio': self.fecha.year })


class CompraLineaItem(fts_models.SearchableModel):
    compra = models.ForeignKey(Compra)
    importe_unitario = models.DecimalField(_('Importe'), decimal_places=2, max_digits=19)
    cantidad = models.CharField(_('Cantidad'), max_length=128, null=True, blank=True)
    detalle = models.TextField(_('Detalle'), null=True, blank=True)

    objects = fts_models.SearchManager(fields=('detalle',), config='spanish')

    def highlight(self, qs):
        """ devuelve self.detalle con los tags de highglight para la búsqueda qs """

        cursor = connection.cursor()
        cursor.execute("SELECT ts_headline('spanish', detalle, to_tsquery('spanish', E'%s'), 'StartSel=<em>, StopSel=</em>, MinWords=300, MaxWords=2000') AS highlighted FROM %s WHERE id = %s" % (qs, CompraLineaItem._meta.db_table, self.id))
        return cursor.fetchone()[0]
       

    def __unicode__(self):
        return "%s (OC: %s)" % (self.detalle, self.compra.oc_numero)
