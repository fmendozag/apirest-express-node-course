from django.urls import path
from seguridad.autorizacion import SegAutorizacionView
from seguridad.cambiar_password import CambiarPasswordInterno
from seguridad.solicitud_cambio_clave import SolicitudCambioClave, solicitar_cambio_clave_form, UsuarioCambiarClave
from seguridad.usuario import LoginPageView, LoginView, logout_user, ConsultaCuenta

urlpatterns = [
    path('login/', LoginPageView.as_view()),
    path('session/', LoginView.as_view()),
    path('salir/', logout_user),
    path('cambiar/password/interno/',CambiarPasswordInterno.as_view()),
    path('solicitud-cambio-clave-email/',SolicitudCambioClave.as_view(),name='solicitud_cambio_clave'),
    path('usuario-cambio-clave/',UsuarioCambiarClave.as_view(),name='usuario_cambio_clave'),
    path('solicitud-cambio-clave-form/<int:id>/<str:ced>/<str:token>/',solicitar_cambio_clave_form,name='solicitud_cambio_clave_form'),
    path('accion-autorizacion/',SegAutorizacionView.as_view(),name='seg_accion_autorizacion'),
    #path('dashboard',login_required(DashboardView.as_view(),login_url='/seguridad/login/'),name='dashboard')
]
