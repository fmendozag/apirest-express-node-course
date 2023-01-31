from django.contrib import admin
from pos.models import *

class PosAperturaCajaAdmin(admin.ModelAdmin):
    list_display = (
        'numero',
        'fecha',
        'caja',
        'total',
        'fecha_cierre',
        'sobrante',
        'faltante',
        'cerrado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('numero',)
    list_filter = (
        'cerrada',
    )

    def cerrado(self, obj):
        return not obj.cerrada
    cerrado.boolean = True
admin.site.register(PosAperturaCaja,PosAperturaCajaAdmin)

class PosCierreAdmin(admin.ModelAdmin):
    list_display = (
        'numero',
        'fecha',
        'fecha_cierre',
        'caja',
        'total_ventas',
        'total_contado',
        'total_credito',
        'total',
        'caja_envio',
        'estad'
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('numero',)
    list_filter = (
        'anulado',
    )

    def estad(self, obj):
        return not obj.anulado
    estad.boolean = True
admin.site.register(PosCierre,PosCierreAdmin)
