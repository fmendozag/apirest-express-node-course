import datetime
import json
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.views.generic.base import View
from contadores.fn_contador import get_contador_sucdiv
from inventario.models import InvConteo, InvConteoDt

class InvConteoView(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        try:
            accion = request.POST.get('accion')
            if accion == 'guardar-conteo':

                with transaction.atomic():

                    json_data = json.loads(request.POST['conteo'])

                    fecha = datetime.datetime.strptime(json_data['fecha'], '%d/%m/%Y')
                    sucursalid = json_data['sucursalid']
                    divisionid = json_data['divisionid']
                    divisaid = json_data['divisionid']
                    detalle = json_data['detalle'].strip()

                    conteo_id = get_contador_sucdiv(
                        'INV_CONTEO-ID-',
                        '{}{}'.format(sucursalid, divisionid[-1])
                    )
                    conteo_numero = get_contador_sucdiv(
                        'INV_CONTEO-NUMBER-',
                        '{}{}'.format(sucursalid, divisionid[-1])
                    )

                    conteo = InvConteo(
                        id=conteo_id,
                        numero=conteo_numero,
                        toma_fisica=json_data['toma_fisicoid'],
                        division_id=divisionid,
                        fecha=fecha,
                        tipo='INV-CON',
                        detalle=detalle
                    )
                    conteo.save()

                    for item in json_data['items']:
                        cantidad = Decimal(item['cantidad'])
                        if cantidad > 0:
                            conteoid_dt_id = get_contador_sucdiv(
                                'INV_TRANSFERENCIAS_DT-ID-',
                                '{}{}'.format(sucursalid, divisionid[-1])
                            )
                            conteo_detalle = InvConteoDt(
                                id=conteoid_dt_id,
                                #toma=transferencia.id,
                                producto_id=item['productoid'],
                                cantidad=cantidad,
                                empaque=item['empaque'],
                                costo=item['costo'],
                                factor=item['factor'],
                                total=round(cantidad * Decimal(item['factor']) * Decimal(item['costo']), 2),
                                sucursalid=sucursalid
                            )
                            conteo_detalle.save()

                    data['resp'] = True
                    return JsonResponse(data, status=200)
        except Exception as e:
            data['error'] = 'error: ' + str(e)
        return JsonResponse(data, status=200)

    # def get(self, request,pk, *args, **kwargs):
    #     data = {}
    #     addUserData(request, data)
    #     try:
    #         try:
    #             transferencia = InvTransferencias.objects.get(pk=pk,anulado=False)
    #         except:
    #             raise Exception("No se econtro transferencia Id.")
    #
    #         inventario = request.user.segusuarioparametro.inventario
    #         if inventario is None:
    #             raise Exception('No se encontro caja asociado al usuario..')
    #
    #         if transferencia.bodega_origen is None:
    #             raise Exception("No se encontro bodega de origen..")
    #
    #         data['inventario'] = inventario
    #         data['sucursal'] = SisSucursales.objects.get(codigo=transferencia.sucursalid)
    #         data['divisiones'] = SisDivisiones.objects.filter(anulado=False)
    #         data['bodegas_origen'] = InvBodegas.objects.filter(anulado=False,transferencia=True)
    #         data['bodegas_destino'] = InvBodegas.objects.filter(anulado=False)
    #
    #         if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
    #             data['disabled'] = True
    #
    #
    #         data['transferencia']=transferencia
    #         return render(request, 'inventario/inv_punto_tranferencia.html', data)
    #     except Exception as e:
    #         messages.add_message(request, 40, str(e))
    #     return redirect('/')
