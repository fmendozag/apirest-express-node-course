from django.contrib import admin

# Register your models here.
from contabilidad.models import *

class AccCuentasAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'codigo',
        'nombre',
        'clase',
        'tipo',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('id','codigo', 'nombre')
    list_filter = (
        'sucursalid',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True
admin.site.register(AccCuentas,AccCuentasAdmin)

class AccAsientosAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'fecha',
        'documentoid',
        'numero',
        'detalle',
        'tipo',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('documentoid', 'numero','detalle')
    list_filter = (
        'sucursalid',
        'tipo',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True
admin.site.register(AccAsientos,AccAsientosAdmin)
