# coding: utf-8
from django.contrib import admin
from gpbweb.core import models

class ReparticionAdmin(admin.ModelAdmin):
    model = models.Reparticion

class CompraLineaItemInline(admin.TabularInline):
    model = models.CompraLineaItem

class CompraAdmin(admin.ModelAdmin):
    model = models.Compra
    inlines = (CompraLineaItemInline)

class ProveedorAdmin(admin.ModelAdmin):
    model = models.Proveedor


admin.site.register(Reparticion, ReparticionAdmin)
admin.site.register(Compra, CompraAdmin)
admin.site.register(Proveedor, ProveedorAdmin)

