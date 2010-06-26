# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Proveedor'
        db.create_table('core_proveedor', (
            ('localidad', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('nombre', self.gf('django.db.models.fields.TextField')(max_length=256, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domicilio', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('cuit', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Proveedor'])

        # Adding model 'Reparticion'
        db.create_table('core_reparticion', (
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['Reparticion'])

        # Adding model 'Compra'
        db.create_table('core_compra', (
            ('proveedor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Proveedor'])),
            ('fecha', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('destino', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Reparticion'])),
            ('orden_compra', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('importe', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('suministro', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Compra'])

        # Adding model 'CompraLineaItem'
        db.create_table('core_compralineaitem', (
            ('compra', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Compra'])),
            ('importe_unitario', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cantidad', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('detalle', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['CompraLineaItem'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Proveedor'
        db.delete_table('core_proveedor')

        # Deleting model 'Reparticion'
        db.delete_table('core_reparticion')

        # Deleting model 'Compra'
        db.delete_table('core_compra')

        # Deleting model 'CompraLineaItem'
        db.delete_table('core_compralineaitem')
    
    
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
            'nombre': ('django.db.models.fields.TextField', [], {'max_length': '256', 'blank': 'True'})
        },
        'core.reparticion': {
            'Meta': {'object_name': 'Reparticion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }
    
    complete_apps = ['core']
