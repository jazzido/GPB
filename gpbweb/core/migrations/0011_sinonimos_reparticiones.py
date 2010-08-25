# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    
    def forwards(self, orm):
        orm.ReparticionSinonimo.objects.create(nombre='DELEG. CABILDO', canonico=orm.Reparticion.objects.get(nombre='DELEGACION CABILDO'))
        orm.ReparticionSinonimo.objects.create(nombre='DELEG. GRAL. DANIEL CERRI', canonico=orm.Reparticion.objects.get(nombre='DELEGACION GRAL. DANIEL CERRI'))
        orm.ReparticionSinonimo.objects.create(nombre='DELEG. NORTE', canonico=orm.Reparticion.objects.get(nombre='DELEGACION NORTE'))
        orm.ReparticionSinonimo.objects.create(nombre='DELEG. VILLA ROSAS', canonico=orm.Reparticion.objects.get(nombre='DELEGACION VILLA ROSAS'))

        orm.ReparticionSinonimo.objects.create(nombre='DEP. CATASTRO', canonico=orm.Reparticion.objects.get(nombre='DEPARTAMENTO CATASTRO'))
        orm.ReparticionSinonimo.objects.create(nombre='DEP. COMPRAS', canonico=orm.Reparticion.objects.get(nombre='DEPARTAMENTO COMPRAS'))
        orm.ReparticionSinonimo.objects.create(nombre='DEP. INSPECCIONES', canonico=orm.Reparticion.objects.get(nombre='DEPARTAMENTO INSPECCIONES'))
        orm.ReparticionSinonimo.objects.create(nombre='DEP. RECAUDACION', canonico=orm.Reparticion.objects.get(nombre='DEPARTAMENTO RECAUDACION'))

        orm.ReparticionSinonimo.objects.create(nombre='DIR. CEREMONIAL', canonico=orm.Reparticion.objects.get(nombre='DIRECCION DE CEREMONIAL'))
        orm.ReparticionSinonimo.objects.create(nombre='DIR. DE TURISMO', canonico=orm.Reparticion.objects.get(nombre='DIRECCION DE TURISMO'))
        orm.ReparticionSinonimo.objects.create(nombre='DIR. GENERAL DE TRANSPORTE', canonico=orm.Reparticion.objects.get(nombre='DIRECCION GENERAL DE TRANSPORTE'))

        orm.ReparticionSinonimo.objects.create(nombre='SEC. DE ECONOMIA Y HACIENDA', canonico=orm.Reparticion.objects.get(nombre='SECRETARIA DE ECONOMIA Y HACIENDA'))
        orm.ReparticionSinonimo.objects.create(nombre='SEC. DE GOBIERNO', canonico=orm.Reparticion.objects.get(nombre='SECRETARIA DE GOBIERNO'))
        orm.ReparticionSinonimo.objects.create(nombre='SEC. DE OBRAS Y SERV. PUBLICOS', canonico=orm.Reparticion.objects.get(nombre='SECRETARIA DE OBRAS Y SERV. PUBLICOS'))
        orm.ReparticionSinonimo.objects.create(nombre='SEC. DE PROMOCION SOCIAL', canonico=orm.Reparticion.objects.get(nombre='SECRETARIA DE PROMOCION SOCIAL'))
        orm.ReparticionSinonimo.objects.create(nombre='SEC. DE SALUD', canonico=orm.Reparticion.objects.get(nombre='SECRETARIA DE SALUD'))
        orm.ReparticionSinonimo.objects.create(nombre='SEC. LEGAL Y TECNICA', canonico=orm.Reparticion.objects.get(nombre='SECRETARIA LEGAL Y TECNICA'))


    def backwards(self, orm):
        "Write your backwards methods here."
    
    models = {
        'core.compra': {
            'Meta': {'object_name': 'Compra'},
            'destino': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Reparticion']"}),
            'fecha': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importe': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'}),
            'orden_compra': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'proveedor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Proveedor']"}),
            'suministro': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
        },
        'core.compralineaitem': {
            'Meta': {'object_name': 'CompraLineaItem'},
            'cantidad': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'compra': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Compra']"}),
            'detalle': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importe_unitario': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'})
        },
        'core.proveedor': {
            'Meta': {'object_name': 'Proveedor'},
            'cuit': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'domicilio': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localidad': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.TextField', [], {'unique': 'True', 'max_length': '256', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'core.reparticion': {
            'Meta': {'object_name': 'Reparticion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'core.reparticionsinonimo': {
            'Meta': {'unique_together': "(('nombre', 'canonico'),)", 'object_name': 'ReparticionSinonimo'},
            'canonico': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sinonimos'", 'to': "orm['core.Reparticion']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.TextField', [], {'unique': 'True', 'max_length': '128'})
        }
    }
    
    complete_apps = ['core']
