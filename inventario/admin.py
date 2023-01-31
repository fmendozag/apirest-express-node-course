from django.contrib import admin

from inventario.models import *

class InvProductosAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'nombre',
        'grupo',
        'clase',
        'empaque',
        'proveedor',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('codigo', 'nombre','nombre_corto')
    list_filter = (
        'grupo',
        'sucursalid',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True

admin.site.register(InvBodegas)

class InvGruposAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'nombre',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('codigo', 'nombre')
    list_filter = (
        'sucursalid',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True
admin.site.register(InvGrupos,InvGruposAdmin)
admin.site.register(InvProductos,InvProductosAdmin)

class InvProductosProxy(InvProductos):
    class Meta:
        proxy = True
        verbose_name = 'Producto precio'
        verbose_name_plural = 'Productos precios'
        managed = False
class InvProductosPorcentajesAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Datos del Producto', {
            'fields': [
                ('codigo','nombre')
            ]
        }),
        ('Costos', {
            'fields': [
                ('costo_compra', 'costo_promedio'),
            ]
        }),
        ('Precios', {
            'fields': [
                ('rentabilidad_costo_contado','web_precio_contado'),
                ('rentabilidad_costo_credito','web_precio_credito'),
            ]
        }),
        ('Valores de comision', {
            'fields': [
                ('comision_pvp_contado','web_comision_contado'),
                ('comision_pvp_credito','web_comision_credito'),
            ]
        }),
    ]

    list_display = (
        'codigo',
        'nombre',
        'web_precio_contado',
        'web_precio_credito',
        'web_comision_contado',
        'web_comision_credito',
        'con_iva',
        'estado',
    )
    list_per_page = 10
    ordering = ('-creadodate',)
    search_fields = ('codigo', 'nombre','nombre_corto')
    list_filter = (
        'sucursalid',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True

    def con_iva(self, obj):
        if obj.impuestoid.strip():
            return True
        return False

    con_iva.boolean = True

    class Media:
        js = (
            '/static/js/calcular_precios.js',
        )
admin.site.register(InvProductosProxy,InvProductosPorcentajesAdmin)
admin.site.register(InvParametroBodegas)


class InvTransferenciasAdmin(admin.ModelAdmin):
    list_display = (
        'numero',
        'fecha',
        'tipo',
        'detalle',
        'bodega_origen',
        'bodega_destino',
        'total',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('numero', 'detalle')
    list_filter = (
        'sucursalid',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True

admin.site.register(InvTransferencias,InvTransferenciasAdmin)


class InvFisicoAdmin(admin.ModelAdmin):
    list_display = (
        'numero',
        'fecha',
        'tipo',
        'detalle',
        'bodega',
        'procesado',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('numero', 'detalle')
    list_filter = (
        'sucursalid',
        'anulado',
    )

    def estado(self, obj):
        return not obj.anulado

    estado.boolean = True


admin.site.register(InvFisico, InvFisicoAdmin)


