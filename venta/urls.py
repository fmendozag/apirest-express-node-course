from django.urls import path

from seguridad.decorators import permiso_modulo
from venta.views import VenDocumentoFactura, VenComisionLiquidacionVentas, get_procesar_facturas, \
    get_consulta_pendientes, VenDocumentoFacturaCotizar, CliCotizacionesPersonalizada

urlpatterns = [
    path('factura/', permiso_modulo()(VenDocumentoFactura.as_view())),
    path('factura/crear', permiso_modulo()(VenDocumentoFactura.as_view())),
    path('comision/liquidacion/', VenComisionLiquidacionVentas.as_view()),
    path('comision/liquidacion/buscar-pendientes/', get_consulta_pendientes),
    path('procesar-factura-detalle',get_procesar_facturas,name='procesar_factura'),
    path('cotizacion-personalizada/', permiso_modulo()(CliCotizacionesPersonalizada.as_view())),
    #path('factura/cotizar/',VenDocumentoFacturaCotizar.as_view(),name='factura_cotizar'),
]
