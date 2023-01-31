from django.contrib import admin
from banco.models import *

class BanBancosAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'codigo',
        'nombre',
        'bodega',
        'ctamayorid',
        'sucursal',
        'division',
        'ventas',
        'cobertura',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('codigo', 'nombre')
    list_filter = (
        'grupo',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True

admin.site.register(BanGrupos)
admin.site.register(BanBancos,BanBancosAdmin)

class BanIngresosAdmin(admin.ModelAdmin):
    list_display = (
        'numero',
        'fecha',
        'asientoid',
        'banco',
        'deudor',
        'tipo',
        'valor',
        'cajaid',
        'creadopor',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('numero', 'deudor__nombre')
    list_filter = (
        'tipo',
        'cajaid',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True
admin.site.register(BanIngresos,BanIngresosAdmin)
admin.site.register(BanIngresosDeudas)

class BanIngresosProxy(BanIngresos):
    class Meta:
        proxy = True
        verbose_name = 'Banco Ingreso Cambiar Fecha'
        verbose_name_plural = 'Banco Ingresos Cambiar Fecha'
        managed = False

class BanIngresosProxyAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Detalle de Banco Ingreso', {
            'fields': [
                ('detalle',),
                ('fecha', 'banco'),
                ('asientoid','creadopor'),
            ]
        }),
    ]

    list_display = (
        'numero',
        'fecha',
        'asientoid',
        'deudor',
        'tipo',
        'valor',
        'cajaid',
        'creadopor',
        'estado',
    )
    list_per_page = 10
    ordering = ('-creadodate',)
    search_fields = ('numero','asientoid', 'deudor__nombre','creadopor')
    list_filter = (
        'tipo',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True

admin.site.register(BanIngresosProxy,BanIngresosProxyAdmin)

class BanBancosCardexAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'fecha',
        'tipo',
        'banco',
        'documentoid',
        'asientoid',
        'detalle',
        'debito',
        'valor',
        'numero',
        'creadopor',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('detalle','asientoid','documentoid')
    list_filter = (
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True
admin.site.register(BanBancosCardex,BanBancosCardexAdmin)


