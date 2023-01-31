from django.urls import path
from pedido.chequear import InformeChequearPedidosView, OrdenPedidoChequearDetalle
from pedido.views import OrdenPedidoVenta, InformeOrdenesPedidosView, OrdenPedidoPuntoVenta
from seguridad.decorators import permiso_modulo

urlpatterns = [
    #path('orden-pedido/', permiso_modulo()(OrdenPedidoVenta.as_view())),
    #path('orden-pedido/<int:pk>', permiso_modulo()(OrdenPedidoVenta.as_view()),name="editar_pedido"),

    path('orden-pedido/', permiso_modulo()(OrdenPedidoPuntoVenta.as_view())),
    path('orden-pedido/<int:pk>', permiso_modulo()(OrdenPedidoPuntoVenta.as_view()),name="editar_pedido"),

    path('ordenes-pedidos/', InformeOrdenesPedidosView.as_view()),
    path('orden-pedido/check-list/', InformeChequearPedidosView.as_view()),
    path('ajax/pedido-orden-detalle/', OrdenPedidoChequearDetalle.as_view()),
]
