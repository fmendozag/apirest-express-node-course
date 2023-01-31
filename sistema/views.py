from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
# Create your views here.
from sistema.models import SisZonas


@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def get_consulta_zona(request):
    data = {'resp': False, 'error': ''}
    if request.method == 'POST':
        try:
            accion = request.POST.get('accion')
        except Exception as e:
            data['error'] = 'error: ' + str(e)
    else:
        try:
            accion = request.GET.get('accion')
            if accion =='zona_buscar':
                tipo = request.GET.get('tipo','')
                zonas = SisZonas.objects.filter(
                    Q(anulado=False),
                    Q(nombre__icontains=request.GET.get('criterio', '')),
                    Q(tipo=tipo)
                ).order_by('nombre')[:15]

                lista_zonas = []
                for z in zonas:
                    lista_zonas.append({
                        "id": z.id,
                        "cod": z.codigo,
                        "nombre": z.nombre
                    })
                return JsonResponse({"items": lista_zonas}, status=200)
        except Exception as e:
            data['error'] = 'error: ' + str(e)
    return JsonResponse(data, status=200)
