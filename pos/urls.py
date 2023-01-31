from django.urls import path
from pos.punto_venta import PosPuntoVentaFactura, PosAperturaCierreCaja, PosPuntoVentaFacturaMovil
from pos.punto_venta_cartilla import PosPuntoVentaCartilla
from pos.punto_venta_imprimir import PosPuntoVentaImprimir
from pos.punto_venta_mayorista import PosPuntoVentaMayoristaFactura
from pos.views import InformeFacturarPedidosView

urlpatterns = [
    path('factura/pedidos/', InformeFacturarPedidosView.as_view()),
    path('factura/pedido/<int:pk>', PosPuntoVentaMayoristaFactura.as_view(),name='facturar_pedido'),
    path('factura/pedido/procesar/', PosPuntoVentaMayoristaFactura.as_view(),name='facturar_pedido'),

    path('punto-venta/factura/', PosPuntoVentaFactura.as_view(),name='punto_venta'),
    path('ajax/caja-apertura/', PosAperturaCierreCaja.as_view(),name='ajax_caja_apertura'),
    path('punto-venta/imprimir/', PosPuntoVentaImprimir.as_view(),name='pos_punto_venta_imprimir'),

    path('punto-venta/cartilla/', PosPuntoVentaCartilla.as_view(),name='punto_venta_cartilla'),
    path('punto-venta/movil/', PosPuntoVentaFacturaMovil.as_view(),name='punto_venta_movil'),
]
