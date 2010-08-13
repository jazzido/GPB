# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'ReparticionSinonimo'
        db.create_table('core_reparticionsinonimo', (
            ('canonico', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sinonimos', to=orm['core.Reparticion'])),
            ('nombre', self.gf('django.db.models.fields.TextField')(unique=True, max_length=128)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['ReparticionSinonimo'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'ReparticionSinonimo'
        db.delete_table('core_reparticionsinonimo')
    
    
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
