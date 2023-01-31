from rest_framework.response import Response
from rest_framework.views import APIView
from cliente.models import CliClientes
from sistema.models import SisParametros

class CliConsultaClientes(APIView):
    def get(self, request, *args, **kwargs):
        data ={}
        try:
            accion = request.GET.get('accion')
            if accion == 'cliente_buscar':
                s = '%{}%'.format(request.GET.get('criterio', ''))
                personas = CliClientes.objects.extra(
                    where=["UPPER([CLI_CLIENTES].[Nombre]) LIKE UPPER(%s)"], params=[s]
                ).filter(
                    anulado=False
                ).order_by('nombre')[:25]
                lista_personas = []
                for p in personas:
                    try:
                        termino = SisParametros.objects.get(pk=p.termino)
                    except:
                        termino = None

                    lista_personas.append({
                        "id": p.id,
                        "cod": p.codigo,
                        "ruc": p.ruc,
                        "nombre": '{} : {}'.format(p.nombre, p.ruc),
                        "precio_lista": p.precio_lista,
                        "precio_activo": p.precio_activo,
                        "lista_precio": p.get_precio_activo_display(),
                        "terminoid": p.termino,
                        "termino_display": termino.nombre if termino is not None else '',
                        "termino_cod": termino.codigo if termino is not None else '',
                        "zona_id": p.zona_id,
                        "cupo": p.cupo,
                        "vendedorid": p.vendedor_id if p.vendedor_id is not None else '',
                        "vendedor": p.vendedor.nombre if p.vendedor_id is not None else '',
                        "tasa_descuento": round(p.tasa_descuento, 2),
                        "tasa_incremento": round(p.tasa_incremento, 2)
                    })
                return Response({"items": lista_personas}, status=200)
        except Exception as e:
            data['error'] = str(e)
        return Response(data, status=200)

