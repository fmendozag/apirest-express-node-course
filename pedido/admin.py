from django.contrib import admin
from pedido.models import VenOrdenPedidos, VenOrdenPedidosDetalle

class VenOrdenPedidosAdmin(admin.ModelAdmin):
    list_display = (
        'id',
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
    search_fields = ('cliente__nombre', 'numero')
    list_filter = (
        'tipo',
        'sucursalid',
        'anulado',
    )

    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True
admin.site.register(VenOrdenPedidos,VenOrdenPedidosAdmin)

class VenOrdenPedidosDetalleAdmin(admin.ModelAdmin):
    list_display = (
        'orden_pedido',
        'producto',
        'bodega',
        'empaque',
        'factor',
        'cantidad',
        'precio',
        'subtotal',
        'impuesto',
        'total',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('orden_pedido__numero', 'producto__nombre')
    list_filter = (
        'bodega',
    )
admin.site.register(VenOrdenPedidosDetalle,VenOrdenPedidosDetalleAdmin)


