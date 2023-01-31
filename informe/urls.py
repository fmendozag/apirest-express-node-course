from django.urls import path

from informe.inventario import InformeTranferenciaView, transferencia_inv_documento
from informe.views import InformeArqueoCajaView, informe_vendedor_comisiones, \
    InformeComisionLiquidacionView, InformeCatalogoView, orden_pedido_documento, InformeLiquidacionVentasView, \
    InformeFacturasCartillasView, InformePuntoVentaFacturasView, informe_orden_pedido, InformeGenerarPlacaProductosView, \
    InformeGeneralFacturasView
from informe.toma_fisica import tomaFisicoConteoDetImprimir, toma_fisica_inv_documento, \
    informe_toma_fisica_detalle_agrupado
from seguridad.decorators import permiso_modulo


urlpatterns = [
    #path('facturas/',permiso_modulo()(InformeFacturasView.as_view()),name="informe_facturas"),
    path('facturas/',permiso_modulo()(InformePuntoVentaFacturasView.as_view()),name="informe_facturas"),
    #path('ventas/facturas',permiso_modulo()(InformePuntoVentaFacturasView.as_view()),name="informe_facturas"),
    path('facturas/cartillas/',permiso_modulo()(InformeFacturasCartillasView.as_view()),name="informe_cartillas"),
    path('arqueo-caja/',permiso_modulo()(InformeArqueoCajaView.as_view()),name="informe_arqueo_caja"),
    path('vendedor/comision/<str:tipo>/<int:pk>/',informe_vendedor_comisiones,name="informe_comisiones_id"),
    path('comision/liquidacion/',InformeComisionLiquidacionView.as_view(),name="informe_comisiones_liquidacion"),
    path('catalogo/clientes/',InformeCatalogoView.as_view(),name="catalogo_clientes"),
    path('orden-pedido/<str:tipo>/<int:pid>/<str:name>', orden_pedido_documento,name="informe_orden_pedido"),
    path('informe_orden_pedido/', informe_orden_pedido,name="informe_orden_pedidos"),
    path('liquidacion/ventas/', InformeLiquidacionVentasView.as_view(),name="informe_liquidacion_ventas"),

    path('transferencia_inventario/', InformeTranferenciaView.as_view()),
    path('transferencia_documento/<str:tipo>/<str:pid>/<str:name>', transferencia_inv_documento,name="informe_transferencia_pdf"),

    path('toma-fisica/detalle/conteo/<str:pid>', tomaFisicoConteoDetImprimir,name="informe_toma_fisica_conteo_pdf"),
    path('toma-fisica/detalle/<str:pid>', toma_fisica_inv_documento,name="informe_toma_fisica_detalle_pdf"),
    path('toma-fisica/detalle/agrupado/<str:pid>', informe_toma_fisica_detalle_agrupado,name="informe_toma_fisica_detalle_agrupado"),

    path('placa/productos/', InformeGenerarPlacaProductosView,name="informe_placa_productos"),
    path('facturas_general/',permiso_modulo()(InformeGeneralFacturasView.as_view()),name = "informe_general")

]
