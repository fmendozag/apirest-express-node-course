from django.urls import path

from sistema.views import get_consulta_zona

urlpatterns = [
    path('zonas/consultar',get_consulta_zona,name="consulta_zona"),
]
