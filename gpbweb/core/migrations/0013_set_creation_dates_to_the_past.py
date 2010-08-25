# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    
    def forwards(self, orm):

        past = datetime.datetime.now() - datetime.timedelta(days=2)

        for p in orm.Proveedor.objects.all():
            p.created_at = past
            p.save()
        
        for p in orm.Reparticion.objects.all():
            p.created_at = past
            p.save()

        for p in orm.Compra.objects.all():
            p.created_at = past
            p.save()
    
    
    def backwards(self, orm):
        "Write your backwards methods here."
    
    models = {
        'core.compra': {
            'Meta': {'object_name': 'Compra'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
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
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'cuit': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'domicilio': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localidad': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.TextField', [], {'unique': 'True', 'max_length': '256', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'core.reparticion': {
            'Meta': {'object_name': 'Reparticion'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
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
