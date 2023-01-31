from django.urls import path
from cliente.views import get_consulta_cliente, CliDocumentoIngresoPago, CliClienteDeudaCartilla, CliClientesListView, \
    cli_cliente_crear, cli_cliente_editar, CliClienteCrear
from seguridad.decorators import permiso_modulo
urlpatterns = [
    path('clientes/consultar',get_consulta_cliente,name="cli_consulta_cliente"),
    path('documento-ingreso/',permiso_modulo()(CliDocumentoIngresoPago.as_view()),name="cli_documento_ingreso"),
    path('estado-cuenta/',permiso_modulo()(CliClienteDeudaCartilla.as_view()),name="cli_estado_cuenta_cartilla"),
    path('clientes/',CliClientesListView.as_view(),name="cli_clientes"),
    path('clientes/crear/',cli_cliente_crear,name="cli_cliente_crear"),
    path('clientes/editar/<str:pk>',cli_cliente_editar,name="cli_cliente_editar"),
    path('clientes/crear/pos/',CliClienteCrear.as_view(),name="cli_cliente_crear_pos"),

]
