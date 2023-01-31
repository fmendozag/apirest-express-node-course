import datetime
import json
import math
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction, connection
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic.base import View
from contabilidad.models import AccAsientos
from contadores.fn_contador import get_contador_sucdiv
from inventario.models import InvTransferencias, InvBodegas, InvTransferenciasDt, InvFisico, InvConteo,InvConteoDt
from sistema.constantes import USER_ALL_PERMISOS, DIVISA_ID
from sistema.funciones import addUserData
from sistema.models import SisSucursales, SisDivisiones

class InvPuntoTranferencia(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        try:
            accion = request.POST.get('accion')
            if accion == 'guardar-transferencia':

                with transaction.atomic():

                    json_data = json.loads(request.POST['transferencia'])
                    opcion = request.POST.get('opcion',None)

                    try:
                        inventario = self.request.user.segusuarioparametro.inventario
                        if inventario is None:
                            raise
                    except:
                        raise Exception("Invalido paramatros bodega destino..")

                    try:
                        bodega_origen = InvBodegas.objects.get(anulado=False, pk=json_data['bodega_origen_id'])
                    except:
                        raise Exception("No se encontro bodega de origen..")

                    try:
                        bodega_destino = InvBodegas.objects.get(anulado=False, pk=json_data['bodega_destino_id'])
                    except:
                        raise Exception("No se encontro bodega de destino..")

                    fecha = datetime.datetime.strptime(json_data['fecha'], '%d/%m/%Y')
                    sucursalid = inventario.sucursal.codigo
                    divisionid = inventario.division.id
                    divisaid = inventario.divisaid
                    detalle = json_data['detalle'].strip()

                    transferencia_id = json_data['id']
                    if transferencia_id in ('',None):
                        tranferencia_id = get_contador_sucdiv(
                            'INV_TRANSFERENCIAS-ID-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )
                        tranferencia_numero = get_contador_sucdiv(
                            'INV_TRANSFERENCIAS-NUMBER-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )
                        transferencia = InvTransferencias(
                            id=tranferencia_id,
                            numero=tranferencia_numero,
                            division_id=divisionid,
                            fecha=fecha,
                            tipo='INV-TR',
                            bodega_origen_id=bodega_origen.id,
                            bodega_destino_id=bodega_destino.id,
                            bodega_numero_origen=bodega_origen.codigo,
                            bodega_numero_destino=bodega_destino.codigo,
                            procesado=False,
                            detalle=detalle
                        )
                        transferencia.save()
                    else:
                        try:
                            transferencia = InvTransferencias.objects.get(pk=transferencia_id,anulado=False)
                        except:
                            raise Exception('No se encontro documento transferencia ID.')

                        transferencia.fecha = fecha
                        transferencia.detalle = detalle
                        transferencia.bodega_origen_id = bodega_origen.id
                        transferencia.bodega_destino_id = bodega_destino.id
                        transferencia.bodega_numero_origen = bodega_origen.codigo
                        transferencia.bodega_numero_destino = bodega_destino.codigo
                        transferencia.save()

                    transferencia.invtransferenciasdt_set.all().delete()

                    if opcion == '1':
                        asientoid = get_contador_sucdiv(
                            'ACC_ASIENTOS-ID-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )
                        asiento_numero = get_contador_sucdiv(
                            'ACC_ASIENTOS-NUMBER-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )
                        transferencia.asientoid = asientoid

                    for item in json_data['items']:
                        cantidad = Decimal(item['cantidad'])
                        if cantidad > 0:
                            tranferenci_dt_id = get_contador_sucdiv(
                                'INV_TRANSFERENCIAS_DT-ID-',
                                '{}{}'.format(sucursalid, divisionid[-1])
                            )
                            tranferencia_detalle = InvTransferenciasDt(
                                id=tranferenci_dt_id,
                                transferencia_id=transferencia.id,
                                producto_id=item['productoid'],
                                cantidad=cantidad,
                                empaque=item['empaque'],
                                costo=round(Decimal(item['costo']),4),
                                factor=round(Decimal(item['factor']),2),
                                total=round(cantidad * Decimal(item['factor']) * Decimal(item['costo']), 2),
                                sucursalid=sucursalid
                            )
                            tranferencia_detalle.save()

                            if opcion == '1':
                                with connection.cursor() as cursor:
                                    cursor.execute(
                                        "{CALL INV_ProductosCardex_Insert_Transferencia(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                        (
                                            tranferencia_detalle.producto_id,
                                            transferencia.bodega_origen.id,
                                            asientoid,
                                            transferencia.id,
                                            transferencia.numero,
                                            fecha,
                                            transferencia.tipo,
                                            detalle,
                                            True,
                                            cantidad * tranferencia_detalle.factor,
                                            tranferencia_detalle.costo,
                                            divisaid,
                                            1,
                                            divisionid,
                                            request.user.username,
                                            sucursalid,
                                            ''
                                        ))

                                    cursor.execute(
                                        "{CALL INV_ProductosCardex_Insert_Transferencia(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                        (
                                            tranferencia_detalle.producto_id,
                                            transferencia.bodega_destino.id,
                                            asientoid,
                                            transferencia.id,
                                            transferencia.numero,
                                            fecha,
                                            transferencia.tipo,
                                            detalle,
                                            False,
                                            cantidad * tranferencia_detalle.factor,
                                            tranferencia_detalle.costo,
                                            divisaid,
                                            1,
                                            divisionid,
                                            request.user.username,
                                            sucursalid,
                                            ''
                                        ))

                    transferencia.total = round(transferencia.invtransferenciasdt_set.aggregate(
                        costo_total=Coalesce(Sum('total'), 0)
                    )['costo_total'],2)
                    transferencia.save()

                    if opcion == '1':
                        total_debe = Decimal(0.00)
                        total_haber = Decimal(0.00)

                        asiento = AccAsientos(
                            id=asientoid,
                            numero=asiento_numero,
                            documentoid=transferencia.id,
                            fecha=fecha,
                            tipo=transferencia.tipo,
                            detalle=detalle,
                            divisionid=divisionid,
                            sucursalid=sucursalid
                        )
                        asiento.save()

                        cta_mayor = transferencia.invtransferenciasdt_set.values(
                            ctamayor=F('producto__ctamayor'),
                        ).annotate(
                            valor=Sum(F('cantidad') * F('factor') * F('costo'))
                        ).filter(cantidad__gt=0).order_by('producto__ctamayor')

                        for cm in cta_mayor:
                            if cm['valor'] > 0:
                                if cm['ctamayor']:
                                    with connection.cursor() as cursor:
                                        valor_base = round(Decimal(cm['valor']) * Decimal(1.00), 4)
                                        cursor.execute(
                                            "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                                asiento.id,
                                                cm['ctamayor'],
                                                detalle,
                                                True,
                                                divisaid,
                                                Decimal(1.00),
                                                Decimal(cm['valor']),
                                                valor_base,
                                                request.user.username,
                                                sucursalid,
                                                ''
                                            ))
                                        total_debe += valor_base

                                        cursor.execute(
                                            "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                                asiento.id,
                                                cm['ctamayor'],
                                                detalle,
                                                False,
                                                divisaid,
                                                Decimal(1.00),
                                                Decimal(cm['valor']),
                                                valor_base,
                                                request.user.username,
                                                sucursalid,
                                                ''
                                            ))
                                        total_haber += valor_base

                        total_debe = math.ceil(total_debe * 100) / 100
                        total_haber = math.ceil(total_haber * 100) / 100

                        if total_debe != total_haber:
                            raise Exception('Asiento desbalanceado. TOTAL DEBE:{}  TOTAL HABER:{}'.format(total_debe, total_haber))

                        transferencia.procesado =True
                        transferencia.estado = '2'
                        transferencia.save()

                    data['resp'] = True
                    return JsonResponse(data, status=200)

            elif accion == 'guardar-transferencia-fisico':
                with transaction.atomic():

                    json_data = json.loads(request.POST['toma_fisico'])

                    try:
                        fisico = InvFisico.objects.get(pk=json_data['id'])
                    except:
                        raise Exception("No se encontró toma fisico ID")

                    try:
                        inventario = self.request.user.segusuarioparametro.inventario
                        if inventario is None:
                            raise
                    except:
                        raise Exception("Invalido paramatros usuario bodega..")

                    try:
                        bodega_origen = InvBodegas.objects.get(anulado=False, pk=json_data['bodega_origen_id'])
                    except:
                        raise Exception("No se encontro bodega de origen..")

                    try:
                        bodega_destino = InvBodegas.objects.get(anulado=False, pk=json_data['bodega_destino_id'])
                    except:
                        raise Exception("No se encontro bodega de destino..")

                    fecha = datetime.datetime.strptime(json_data['fecha'], '%d/%m/%Y')
                    sucursalid = fisico.sucursalid
                    divisionid = fisico.division_id
                    divisaid = DIVISA_ID
                    detalle = json_data['detalle'].strip()

                    tranferencia_id = get_contador_sucdiv(
                        'INV_TRANSFERENCIAS-ID-',
                        '{}{}'.format(sucursalid, divisionid[-1])
                    )
                    tranferencia_numero = get_contador_sucdiv(
                        'INV_TRANSFERENCIAS-NUMBER-',
                        '{}{}'.format(sucursalid, divisionid[-1])
                    )
                    asientoid = get_contador_sucdiv(
                        'ACC_ASIENTOS-ID-',
                        '{}{}'.format(sucursalid, divisionid[-1])
                    )
                    asiento_numero = get_contador_sucdiv(
                        'ACC_ASIENTOS-NUMBER-',
                        '{}{}'.format(sucursalid, divisionid[-1])
                    )

                    transferencia = InvTransferencias(
                        id=tranferencia_id,
                        numero=tranferencia_numero,
                        asientoid=asientoid,
                        division_id=divisionid,
                        fecha=fecha,
                        tipo='INV-TRF',
                        bodega_origen_id=bodega_origen.id,
                        bodega_destino_id=bodega_destino.id,
                        bodega_numero_origen=bodega_origen.codigo,
                        bodega_numero_destino=bodega_destino.codigo,
                        procesado=False,
                        detalle=detalle
                    )
                    transferencia.save()

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
                        asientoid=asientoid,
                        toma_fisica_id=fisico.id,
                        fecha=fecha,
                        tipo='INV-CON',
                        detalle=detalle,
                        procesado=True,
                        estado='2',
                        sucursalid=sucursalid,
                        division_id=divisionid
                    )
                    conteo.save()

                    for item in json_data['items']:
                        cantidad = Decimal(item['cantidad']) if Decimal(item['cantidad']) > 0 else abs(Decimal(item['cantidad']))
                        if cantidad > 0 and item['seleccionado']:
                            tranferenci_dt_id = get_contador_sucdiv(
                                'INV_TRANSFERENCIAS_DT-ID-',
                                '{}{}'.format(sucursalid, divisionid[-1])
                            )
                            tranferencia_detalle = InvTransferenciasDt(
                                id=tranferenci_dt_id,
                                transferencia_id=transferencia.id,
                                producto_id=item['productoid'],
                                cantidad=cantidad,
                                empaque=item['empaque'],
                                costo=item['costo'],
                                factor=item['factor'],
                                total=round(cantidad * Decimal(item['factor']) * Decimal(item['costo']), 2),
                                sucursalid=sucursalid
                            )
                            tranferencia_detalle.save()

                            conteo_dt_id = get_contador_sucdiv(
                                'INV_CONTEO_DT-ID-',
                                '{}{}'.format(sucursalid, divisionid[-1])
                            )

                            conteo_detalle = InvConteoDt(
                                id=conteo_dt_id,
                                conteo_id=conteo.id,
                                producto_id=item['productoid'],
                                stock=item['stock'],
                                cantidad=item['fisico_stock'],
                                empaque=item['empaque'],
                                factor=item['factor'],
                                total_unidades=round(cantidad * Decimal(item['factor']), 2),
                                diferencia=item['diferencia'],
                                sucursalid=sucursalid,
                                ajuste=True,
                                transferencia=True,
                                procesado=True
                            )
                            conteo_detalle.save()

                            fisico.invfisicoproductos_set.filter(
                                anulado=False,
                                producto_id=item['productoid']
                            ).update(
                                procesado=True
                            )

                            with connection.cursor() as cursor:
                                cursor.execute(
                                    "{CALL INV_ProductosCardex_Insert_Transferencia(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                    (
                                        tranferencia_detalle.producto_id,
                                        transferencia.bodega_origen.id,
                                        asientoid,
                                        transferencia.id,
                                        transferencia.numero,
                                        fecha,
                                        transferencia.tipo,
                                        detalle,
                                        True,
                                        cantidad * tranferencia_detalle.factor,
                                        tranferencia_detalle.costo,
                                        divisaid,
                                        1,
                                        divisionid,
                                        request.user.username,
                                        sucursalid,
                                        ''
                                    ))


                                cursor.execute(
                                    "{CALL INV_ProductosCardex_Insert_Transferencia(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                    (
                                        tranferencia_detalle.producto_id,
                                        transferencia.bodega_destino.id,
                                        asientoid,
                                        transferencia.id,
                                        transferencia.numero,
                                        fecha,
                                        transferencia.tipo,
                                        detalle,
                                        False,
                                        cantidad * tranferencia_detalle.factor,
                                        tranferencia_detalle.costo,
                                        divisaid,
                                        1,
                                        divisionid,
                                        request.user.username,
                                        sucursalid,
                                        ''
                                    ))

                    transferencia.total = round(transferencia.invtransferenciasdt_set.aggregate(
                        costo_total=Coalesce(Sum('total'), 0)
                    )['costo_total'],2)
                    transferencia.save()

                    total_debe = Decimal(0.00)
                    total_haber = Decimal(0.00)

                    asiento = AccAsientos(
                        id=asientoid,
                        numero=asiento_numero,
                        documentoid=transferencia.id,
                        fecha=fecha,
                        tipo=transferencia.tipo,
                        detalle=detalle,
                        divisionid=divisionid,
                        sucursalid=sucursalid
                    )
                    asiento.save()

                    cta_mayor = transferencia.invtransferenciasdt_set.values(
                        ctamayor=F('producto__ctamayor'),
                    ).annotate(
                        valor=Sum(F('cantidad') * F('factor') * F('costo'))
                    ).filter(cantidad__gt=0).order_by('producto__ctamayor')

                    for cm in cta_mayor:
                        if cm['valor'] > 0:
                            if cm['ctamayor']:
                                with connection.cursor() as cursor:
                                    valor_base = round(Decimal(cm['valor']) * Decimal(1.00), 4)
                                    cursor.execute(
                                        "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                            asiento.id,
                                            cm['ctamayor'],
                                            detalle,
                                            True,
                                            divisaid,
                                            Decimal(1.00),
                                            Decimal(cm['valor']),
                                            valor_base,
                                            request.user.username,
                                            sucursalid,
                                            ''
                                        ))
                                    total_debe += valor_base

                                    cursor.execute(
                                        "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                            asiento.id,
                                            cm['ctamayor'],
                                            detalle,
                                            False,
                                            divisaid,
                                            Decimal(1.00),
                                            Decimal(cm['valor']),
                                            valor_base,
                                            request.user.username,
                                            sucursalid,
                                            ''
                                        ))
                                    total_haber += valor_base

                    total_debe = math.ceil(total_debe * 100) / 100
                    total_haber = math.ceil(total_haber * 100) / 100

                    if total_debe != total_haber:
                        raise Exception('Asiento desbalanceado. TOTAL DEBE:{}  TOTAL HABER:{}'.format(total_debe, total_haber))

                    transferencia.procesado =True
                    transferencia.estado = '2'
                    transferencia.save()

                    if not fisico.invfisicoproductos_set.filter(anulado=False,procesado=False).exists():
                        fisico.estado = '2'
                        fisico.procesado = True
                        fisico.save()

                    data['resp'] = True
                    return JsonResponse(data, status=200)
        except Exception as e:
            data['error'] = 'error: ' + str(e)
        return JsonResponse(data, status=200)

    def get(self, request,pk, *args, **kwargs):
        data = {}
        addUserData(request, data)
        try:
            try:
                transferencia = InvTransferencias.objects.get(pk=pk,anulado=False)
            except:
                raise Exception("No se econtro transferencia Id.")

            inventario = request.user.segusuarioparametro.inventario
            if inventario is None:
                raise Exception('No se encontro caja asociado al usuario..')

            if transferencia.bodega_origen is None:
                raise Exception("No se encontro bodega de origen..")

            data['inventario'] = inventario
            data['sucursal'] = SisSucursales.objects.get(codigo=transferencia.sucursalid)
            data['divisiones'] = SisDivisiones.objects.filter(anulado=False)
            data['bodegas_origen'] = InvBodegas.objects.filter(anulado=False,transferencia=True)
            data['bodegas_destino'] = InvBodegas.objects.filter(anulado=False)

            if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                data['disabled'] = True

            data['transferencia']=transferencia
            return render(request, 'inventario/inv_punto_tranferencia.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')

class InvPuntoTransferenciaChequear(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        try:
            accion = request.POST.get('accion')

            if accion == 'update-transferencia-anular':

                transferencia_id = request.POST.get('transferencia_id')
                estado = request.POST.get('estado')
                motivo = request.POST.get('motivo','')

                try:
                    transferencia = InvTransferencias.objects.get(pk=transferencia_id)
                except:
                    raise Exception('No se encontro la transferencia')

                if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                    if transferencia.creadopor.strip().upper() != request.user.username.strip().upper():
                        raise Exception("No se permite anular el pedido para el usuario actual..")

                if not transferencia.estado in '2':
                    transferencia.estado = estado
                    transferencia.anuladonota =motivo
                    transferencia.anuladodate = datetime.datetime.now()
                    transferencia.anuladopor = request.user.username
                    transferencia.save()

                    data['resp'] = True
                    return JsonResponse(data, status=200)
                else:
                    raise Exception('No se puede anular la transferencia')

        except Exception as e:
            data['error'] = 'error: ' + str(e)
        return JsonResponse(data, status=200)
