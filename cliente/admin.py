from django.contrib import admin

from cliente.models import *

class CliClientesAdmin(admin.ModelAdmin):
    list_display = (
        'ruc',
        'nombre',
        'grupo',
        'ciudad',
        'zona',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('ruc', 'nombre')
    list_filter = (
        'sucursalid',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True
admin.site.register(CliRubros)
admin.site.register(CliGrupos)
admin.site.register(CliClientes,CliClientesAdmin)

class CliClientesDeudasAdmin(admin.ModelAdmin):
    list_display = (
        'fecha',
        'numcartilla',
        'cliente',
        'documentoid',
        'tipo',
        'asientoid',
        'valor',
        'saldo',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('numcartilla', 'cliente__nombre','documentoid')
    list_filter = (
        'tipo',
        'sucursalid',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True

admin.site.register(CliClientesDeudas,CliClientesDeudasAdmin)

class CliCotizacionesAdmin(admin.ModelAdmin):
    list_display = (
        'numero',
        'fecha',
        'tipo',
        'cliente',
        'vendedor',
        'subtotal',
        'impuesto',
        'total',
        'caja',
        'estado'
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('numero','cliente__ruc', 'cliente__nombre')
    list_filter = (
        'tipo',
        'caja',
        'sucursalid',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True

admin.site.register(CliCotizaciones,CliCotizacionesAdmin)

class CliCotizacionesDetalleAdmin(admin.ModelAdmin):
    list_display = (
        'cotizacion',
        'producto',
        'cantidad',
        'precio',
        'subtotal',
        'impuesto',
        'total',
        'estado'
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('cotizacion__numero','producto__nombre')
    list_filter = (
        'sucursalid',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True

admin.site.register(CliCotizacionesDetalle,CliCotizacionesDetalleAdmin)




