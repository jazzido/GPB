# coding: utf-8
from django.contrib import admin
from gpbweb.core import models

class ReparticionAdmin(admin.ModelAdmin):
    model = models.Reparticion

class ReparticionSinonimoAdmin(admin.ModelAdmin):
    model = models.ReparticionSinonimo

class CompraLineaItemInline(admin.TabularInline):
    model = models.CompraLineaItem

class CompraAdmin(admin.ModelAdmin):
    model = models.Compra
    inlines = (CompraLineaItemInline,)

class ProveedorAdmin(admin.ModelAdmin):
    model = models.Proveedor


admin.site.register(models.Reparticion, ReparticionAdmin)
admin.site.register(models.ReparticionSinonimo, ReparticionSinonimoAdmin)
admin.site.register(models.Compra, CompraAdmin)
admin.site.register(models.Proveedor, ProveedorAdmin)

