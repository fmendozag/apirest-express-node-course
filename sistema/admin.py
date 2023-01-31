from django.contrib import admin
from sistema.models import *

class SisDivisionesAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'nombre',
        'ruc_sri',
        'nombre_comercial_sri',
        'gerente',
        'informal',
        'estado',
    )
    list_per_page = 20
    ordering = ('codigo',)
    search_fields = ('codigo', 'nombre')
    list_filter = (
        'tipo',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True

admin.site.register(SisDivisiones,SisDivisionesAdmin)
class SisZonasAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'nombre',
        'tipo',
        'estado',
    )
    list_per_page = 20
    ordering = ('codigo',)
    search_fields = ('codigo', 'nombre')
    list_filter = (
        'tipo',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True
admin.site.register(SisZonas,SisZonasAdmin)
admin.site.register(SisSucursales)

class SisParametrosAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'nombre',
        'tipo',
        'valor',
        'extradata',
        'sucursal',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('codigo', 'nombre')
    list_filter = (
        'sucursal',
        'tipo',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True
admin.site.register(SisParametros,SisParametrosAdmin)
