from django.db.models import Q, Sum, Count, Max
from django.db.models.functions import Coalesce
from django.http import JsonResponse

from inventario.models import InvProductosEmpaques, InvProductos

def get_productos_empaque(request):
    data = {'resp': False, 'error': ''}
    if request.method == 'GET':
        try:
            accion = request.GET.get('accion', '')
            if accion == 'p-empaques':
                empaques = InvProductosEmpaques.objects.filter(
                    producto_id=request.GET.get('producto_id'),
                    producto__anulado=False
                ).exclude(
                    nombre__icontains=request.GET.get('empaque')
                ).exclude(
                    codigo='N'
                ).exclude(
                    codigo_barra=''
                ).order_by('factor')

                lista_empaques=[]
                for e in empaques:
                    lista_empaques.append({
                        'empaque_id': str(e.codigo_barra).strip(),
                        'empaque_codigo': str(e.codigo).strip(),
                        'codigo_barra': e.codigo_barra.strip(),
                        'empaque': e.nombre.lower().strip(),
                        'factor': round(e.factor, 2)
                    })
                data['empaques'] = lista_empaques
                data['resp'] = True
                return JsonResponse(data, status=200)

            if accion == 'p-buscar-productos':
                s = '%{}%'.format(request.GET.get('criterio', ''))

                productos = InvProductos.objects.filter(
                    anulado=False
                ).extra(
                    where=["UPPER([INV_PRODUCTOS].[Nombre]) LIKE UPPER(%s)"], params=[s]
                ).annotate(
                    stock=Coalesce(Sum('invpdbodegastock__stock'), 0),
                    precio_und=Max('precio4'),
                    precio_doc=Max('precio3'),
                    precio_cja=Max('precio1'),
                    formato=Max('descripcion'),
                ).values(
                    'id', 'codigo', 'nombre', 'formato','stock','precio_und','precio_doc','precio_cja'
                ).annotate(
                    cant=Count('id')
                ).order_by(
                    'nombre'
                )[:10]

                lista_productos = []
                for p in productos:
                    lista_productos.append({
                        "productoid": p['id'],
                        "codigo": p['codigo'],
                        "nombre": p['nombre'],
                        "formato": p['formato'],
                        "precio_und": round(p['precio_und'], 2),
                        "precio_doc": round(p['precio_doc'], 2),
                        "precio_cja": round(p['precio_cja'], 2),
                        "stock": round(p['stock'],2)
                    })

                data['productos'] = lista_productos
                data['resp'] = True
                return JsonResponse(data, status=200)
        except Exception as e:
            data['error'] = str(e)
    return JsonResponse(data, status=200)
