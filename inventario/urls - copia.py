from django.urls import path
from inventario.filtro_punto_cartilla import get_punto_venta_cartilla_empaques
from inventario.filtro_punto_pedido import get_punto_pedido_empaques
from inventario.filtro_punto_venta import get_punto_venta_empaques
from inventario.placa_precios import InvPlacaPrecios
from inventario.punto_transferencias import InvPuntoTranferencia, InvPuntoTransferenciaChequear
from inventario.toma_fisico import InvInformeTomaFisicoListView, inv_toma_fisica_crear, InvTomaFisicoDetalle \
    , InvTomaFisicoConteo, inv_get_detalle_toma_fisica, InvTomaFisicoNoExistente
from inventario.views import get_consulta_producto, get_procesar_precios

urlpatterns = [
    path('productos/consultar',get_consulta_producto,name="consulta_producto"),
    path('productos/precios',get_procesar_precios,name="procesar_precios"),

    # path('ajax/codigo-barra/',get_productos_empaque,name="punto_pedido_cod_barra"),
    # path('ajax/consultar/',get_productos_empaque,name="punto_pedido_consultar"),

    path('ajax/pedido/codigo-barra/',get_punto_pedido_empaques,name="punto_pedido_cod_barra"),
    path('ajax/pedido/consultar/',get_punto_pedido_empaques,name="punto_pedido_consultar"),

    path('ajax/punto-venta/codigo-barra/',get_punto_venta_empaques,name="punto_venta_cod_barra"),
    path('ajax/punto-venta/consultar/',get_punto_venta_empaques,name="punto_venta_consultar"),

    path('ajax/punto-venta/cartilla/codigo-barra/',get_punto_venta_cartilla_empaques,name="punto_venta_cartilla_cod_barra"),
    path('ajax/punto-venta/cartilla/consultar/',get_punto_venta_cartilla_empaques,name="punto_venta_cartilla_consultar"),

    path('ajax/punto/transferencia/',InvPuntoTransferenciaChequear.as_view(),name="inv_transferencia_chequear"),
    path('punto-tranferencia/<str:pk>',InvPuntoTranferencia.as_view(),name="inv_punto_tranferencia"),
    path('punto-tranferencia/crear/',InvPuntoTranferencia.as_view(),name="inv_punto_tranferencia_crear"),

    path('fisico/',InvInformeTomaFisicoListView.as_view(),name="inv_informe_toma_fisico"),
    path('fisico/detalle/<str:pk>',InvTomaFisicoDetalle.as_view(),name="inv_toma_fisico_detalle"),
    path('fisico/conteo/<str:pk>',InvTomaFisicoConteo.as_view(),name="inv_toma_fisico_conteo"),
    path('fisico/no-existente/<str:pk>',InvTomaFisicoNoExistente.as_view(),name="inv_toma_fisico_no_existente"),
    path('fisico/crear/',inv_toma_fisica_crear,name="inv_toma_fisico_crear"),

    path('fisico/ingreso_egreso/',InvTomaFisicoConteo.as_view(),name="inv_toma_fisico_ingreso_egreso"),
    path('ajax/toma-fisica/detalle/consultar/',inv_get_detalle_toma_fisica,name="inv_toma_fisico_detalle_consultar"),

    path('generar-placa/precios/',InvPlacaPrecios.as_view(),name="inv_generar_placa_precios"),
    path('ajax/punto-venta/precio-codigo-barra/',get_punto_venta_empaques,name="punto_venta_precio_codigo_barra"),
    path('ajax/punto-venta/precio-autocomplete/',get_punto_venta_empaques,name="punto_venta_precio_autocomplete")

]
