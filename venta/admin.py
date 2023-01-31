from django.contrib import admin
from venta.models import *

class VenFacturasAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'numcartilla',
        'numero',
        'ruc',
        'cliente',
        'fecha',
        'tipo',
        'subtotal',
        'total',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('numcartilla', 'cliente__nombre','numero')
    list_filter = (
        'tipo',
        'sucursalid',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True

admin.site.register(VenFacturas,VenFacturasAdmin)
admin.site.register(VenFacturasDetalle)


class VenLiquidacionComisionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'numero',
        'fecha',
        'tipo',
        'total',
        'vendedor',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('numero', 'vendedor__nombre')
    list_filter = (
        'tipo',
        'sucursalid',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True

admin.site.register(VenLiquidacionComision,VenLiquidacionComisionAdmin)
admin.site.register(VenLiquidacionComisionDetalle)

class VenLiquidacionMovimientosAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'numero',
        'documentoid',
        'fecha',
        'numcartilla',
        'cliente',
        'vendedor',
        'valor_credito',
        'valor',
        'tipo',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('numero','numcartilla','vendedor__nombre','documentoid','cliente__nombre')
    list_filter = (
        'tipo',
        'sucursalid',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True
admin.site.register(VenLiquidacionMovimientos,VenLiquidacionMovimientosAdmin)
