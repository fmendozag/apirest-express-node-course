from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
# Create your views here.
from empleado.models import EmpEmpleados

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def get_consulta_empleado(request):
    data = {'resp': False, 'error': ''}
    if request.method == 'POST':
        try:
            accion = request.POST.get('accion')
        except Exception as e:
            data['error'] = 'error: ' + str(e)
    else:
        try:
            accion = request.GET.get('accion')
            if accion =='empleado_buscar':
                tipo = request.GET.get('tipo','')
                criterio = {
                    "nombre__icontains" : request.GET.get('criterio', ''),
                     tipo : True
                }
                def queries(filters):
                    return [Q(**{k: v}) for k, v in filters.items() if v]

                empleados = EmpEmpleados.objects.filter(
                    anulado=False,
                    *queries(criterio)
                ).order_by('nombre')[:15]

                lista_empleados = []
                for e in empleados:
                    lista_empleados.append({
                        "id": e.id,
                        "cod": e.codigo,
                        "nombre": e.nombre
                    })
                return JsonResponse({"items": lista_empleados}, status=200)
        except Exception as e:
            data['error'] = 'error: ' + str(e)
    return JsonResponse(data, status=200)

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def get_ajax_consulta_vendedor(request):
    data = {'resp': False, 'error': ''}
    if request.method == 'GET':
        try:
            tipo = request.GET.get('tipo', '')
            criterio = {
                "nombre__icontains": request.GET.get('search', ''),
                tipo: True
            }
            def queries(filters):
                return [Q(**{k: v}) for k, v in filters.items() if v]

            empleados = EmpEmpleados.objects.filter(
                anulado=False,
                *queries(criterio)
            ).order_by('nombre')[:20]

            lista_empleados = []
            for e in empleados:
                lista_empleados.append({
                    "id": e.id,
                    "text": e.nombre
                })
            return JsonResponse({"items": lista_empleados}, status=200)
        except Exception as e:
            data['error'] = 'error: ' + str(e)
    return JsonResponse(data, status=200)
