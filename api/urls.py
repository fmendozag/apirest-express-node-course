from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from api.inventario import InvConsultaProductos, InvTransferencia, InvConsultaProductosClientes, InvTomaFisico
from api.inventario_data import InvProductosMovilView
from api.pos import PosSincronizarFacturas
from api.views import CustomTokenObtainPairView

urlpatterns = [
    path(
        'token/create/',
        jwt_views.TokenObtainPairView.as_view(),
        name='token-create'
    ),
    path(
        'token/refresh/',
        jwt_views.TokenRefreshView.as_view(),
        name='token-refresh'
    ),
    path('users/login/', CustomTokenObtainPairView.as_view(), name='hello'),
    path('prueba/', CustomTokenObtainPairView.as_view(), name='prueba'),

    path('inv/consultar/productos/', InvConsultaProductos.as_view(), name='consultar_productos'),
    path('inv/transferencia/crear/<str:accion>/<str:bodega_id>', InvTransferencia.as_view(), name='inv_tranferencia_crear'),
    path('inv/consultar/productos/clientes/', InvConsultaProductosClientes.as_view(), name='inv_consultar_producto_clientes'),


    path('inv/consultar/toma-fisicos/', InvTomaFisico.as_view(), name='inv_consultar_toma_fisicos'),
    path('inv/toma-fisico/crear/<str:accion>/<str:pk>', InvTomaFisico.as_view(), name='inv_toma_fisico_crear'),

    path('inv/productos/movil/', InvProductosMovilView.as_view(), name='inv_productos_movil'),
    path('pos/sincronizar/facturas/<str:accion>/', PosSincronizarFacturas.as_view(), name='inv_sincronizar_facturas'),
]
