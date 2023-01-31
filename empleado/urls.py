from django.urls import path

from empleado.views import get_consulta_empleado, get_ajax_consulta_vendedor

urlpatterns = [
    path('empleados/consultar',get_consulta_empleado,name="consulta_empleado"),
    path('empleados/comision',get_ajax_consulta_vendedor,name="consulta_empleado"),
]
