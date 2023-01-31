import datetime
import json
import math
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction, connection
from django.db.models import Q, Sum, F, Count
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView
from contabilidad.models import AccAsientos
from contadores.fn_contador import get_contador_sucdiv
from inventario.forms import InvTomaFisicoForm
from inventario.models import InvFisico, InvBodegas, InvProductos, InvIngresos, InvConteo, InvEgresos, \
    InvEgresosProductos, InvConteoDt, InvIngresosProductos, InvRubros, InvPdBodegaStock
from sistema.constantes import USER_ALL_PERMISOS, DIVISA_ID
from sistema.funciones import addUserData
from sistema.models import SisDivisiones, SisSucursales
from django.views.generic.base import View
from django.contrib import messages

class InvInformeTomaFisicoListView(LoginRequiredMixin,ListView):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    model = InvFisico
    template_name = 'inventario/inv_informe_toma_fisico.html'  # Default: <app_label>/<model_name>_list.html
    context_object_name = 'fisicos'  # Default: object_list
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        addUserData(self.request, context)

        s = self.request.GET.get('s', '')
        divisionid = self.request.GET.get('divisionid', '')
        bodegaid = self.request.GET.get('bodegaid', '')
        usuarioid = self.request.GET.get('usuarioid', '')

        inicio = self.request.GET.get('inicio', '')
        final = self.request.GET.get('final', '')

        url = '&s={}&inicio={}&final={}&divisionid={}&usuarioid={}&bodegaid={}'.format(
          s,inicio, final,divisionid,usuarioid,bodegaid
        )
        context['url'] = url
        context['s'] = s
        context['inicio'] = inicio
        context['final'] = final
        context['divisionid'] = divisionid
        context['bodegaid'] = bodegaid
        context['usuarioid'] = usuarioid

        context['divisiones'] = SisDivisiones.objects.all()
        context['bodegas'] = InvBodegas.objects.filter(anulado=False)
        context['usuarios'] = User.objects.filter(is_active=True)
        return context

    def get_queryset(self, **kwargs):
        search = self.request.GET.get('s', '')
        criterio = {
            'procesado' : bool(int(self.request.GET.get('procesado', 0))),
            'division_id': self.request.GET.get('divisionid', ''),
            'creadopor': self.request.GET.get('usuarioid', ''),
            'bodega_id': self.request.GET.get('bodegaid', '')
        }

        inicio = self.request.GET.get('inicio', '')
        final = self.request.GET.get('final', '')

        try:
            inicio = datetime.datetime.strptime(inicio, '%Y-%m-%d').date() if inicio else datetime.date.today()
            final = datetime.datetime.strptime(final, '%Y-%m-%d').date() if final else datetime.date.today()
            date_range = (
                datetime.datetime.combine(inicio, datetime.datetime.min.time()),
                datetime.datetime.combine(final, datetime.datetime.max.time())
            )
            criterio['fecha__date__range'] = date_range
        except:
            pass

        def queries(filters):
            return [Q(**{k: v}) for k, v in filters.items() if v]

        return InvFisico.objects.filter(
            Q(anulado=False),
            Q(numero__icontains=search) |
            Q(detalle__icontains=search),
            *queries(criterio)
        )

class InvTomaFisicoDetalle(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request,pk, *args, **kwargs):
        data = {}
        addUserData(request, data)
        try:
            try:
                toma_fisico = InvFisico.objects.get(pk=pk,anulado=False)
            except:
                raise Exception("No se econtro la toma fisica Id.")

            if toma_fisico.bodega is None:
                raise Exception("No se encontro bodega..")

            data['sucursal'] = SisSucursales.objects.get(codigo=toma_fisico.sucursalid)
            data['divisiones'] = SisDivisiones.objects.filter(anulado=False)
            data['bodegas_origen'] = InvBodegas.objects.filter(anulado=False,transferencia=True)
            data['bodegas_destino'] = InvBodegas.objects.filter(anulado=False)

            if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                data['disabled'] = True


            data['toma_fisico']=toma_fisico
            return render(request, 'inventario/inv_toma_fisico_detalle.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')

class InvTomaFisicoConteo(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        try:
            accion = request.POST.get('accion')
            if accion == 'guardar-ingreso-egreso':

                with transaction.atomic():

                    json_data = json.loads(request.POST['toma_fisico'])
                    try:
                        fisico = InvFisico.objects.get(pk=json_data['id'])
                    except:
                        raise Exception("No se encontró toma fisico ID")

                    fecha = datetime.datetime.strptime(json_data['fecha'], '%d/%m/%Y')
                    sucursalid = fisico.sucursalid
                    divisionid = fisico.division_id
                    divisaid = DIVISA_ID
                    detalle = json_data['detalle'].strip()

                    #lista_egresos = [item for item in json_data['items'] if Decimal(item['cantidad']) > 0]
                    lista_egresos = []
                    lista_ingresos = [item for item in json_data['items'] if Decimal(item['cantidad']) > 0]

                    if lista_egresos:

                        asientoid = get_contador_sucdiv(
                            'ACC_ASIENTOS-ID-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )
                        asiento_numero = get_contador_sucdiv(
                            'ACC_ASIENTOS-NUMBER-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )

                        egresos_id = get_contador_sucdiv(
                            'INV_EGRESOS-ID-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )
                        egresos_numero = get_contador_sucdiv(
                            'INV_EGRESOS-NUMBER-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )

                        egresos = InvEgresos(
                            id=egresos_id,
                            numero=egresos_numero,
                            asientoid=asientoid,
                            bodega_id=fisico.bodega.id,
                            bodega_num=fisico.bodega.codigo,
                            division_id=divisionid,
                            fecha=fecha,
                            tipo='INV-EG',
                            detalle=detalle,
                            sucursalid=sucursalid
                        )
                        egresos.save()

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

                        for item in lista_egresos:
                            cantidad = abs(Decimal(item['cantidad']))
                            if cantidad != 0:

                                egresos_dt_id = get_contador_sucdiv(
                                    'INV_EGRESOS_DT-ID-',
                                    '{}{}'.format(sucursalid, divisionid[-1])
                                )
                                producto = InvProductos.objects.get(pk=item['productoid'])

                                egresos_detalle = InvEgresosProductos(
                                    id=egresos_dt_id,
                                    egreso_id=egresos.id,
                                    cta_mayor_id=producto.ctamayor.id,
                                    producto_id=producto.id,
                                    stock=item['stock'],
                                    cantidad=cantidad,
                                    empaque=item['empaque'],
                                    costo=producto.costo_promedio,
                                    factor=item['factor'],
                                    sucursalid=sucursalid
                                )
                                egresos_detalle.save()

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
                                    egreso=True,
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
                                        "{CALL INV_ProductosCardex_Insert_Conteo(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                        (
                                            producto.id,
                                            egresos.bodega_id,
                                            asientoid,
                                            egresos.id,
                                            egresos.numero,
                                            fecha,
                                            egresos.tipo,
                                            detalle,
                                            True,
                                            round(egresos_detalle.cantidad * egresos_detalle.factor, 2),
                                            egresos_detalle.costo,
                                            divisaid,
                                            1,
                                            divisionid,
                                            request.user.username,
                                            sucursalid,
                                            ''
                                        ))

                        egresos.valor_base = round(egresos.invegresosproductos_set.aggregate(
                            valor=Coalesce(Sum(F('cantidad') * F('factor') * F('costo')), 0)
                        )['valor'],2)
                        egresos.save()

                        total_debe = Decimal(0.00)
                        total_haber = Decimal(0.00)

                        rubro = InvRubros.objects.get(anulado=False, codigo='EGR-008')

                        with connection.cursor() as cursor:
                            cursor.execute(
                                "{CALL INV_EgresosRubros_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                (
                                    egresos.id,
                                    rubro.id,
                                    detalle,
                                    rubro.ctadebe_id,
                                    divisaid,
                                    Decimal('1.00'),
                                    round(egresos.valor_base * Decimal(1.00), 2),
                                    True,
                                    request.user.username,
                                    sucursalid,
                                    ''
                                ))

                        asiento = AccAsientos(
                            id=asientoid,
                            numero=asiento_numero,
                            documentoid=egresos.id,
                            fecha=fecha,
                            tipo=egresos.tipo,
                            detalle=detalle,
                            divisionid=divisionid,
                            sucursalid=sucursalid
                        )
                        asiento.save()

                        ctas_mayor = egresos.invegresosproductos_set.filter(cantidad__gt=0).values(
                            'cta_mayor_id'
                        ).annotate(
                            valor=Coalesce(Sum(F('cantidad') * F('factor') * F('costo')), 0)
                        ).order_by('cta_mayor_id')

                        for cm in ctas_mayor:
                            if cm['valor'] > 0:
                                if cm['cta_mayor_id']:
                                    with connection.cursor() as cursor:
                                        valor_base = round(Decimal(cm['valor']) * Decimal(1.00), 2)
                                        cursor.execute(
                                            "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                                asiento.id,
                                                cm['cta_mayor_id'],
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

                        with connection.cursor() as cursor:
                            valor_base = round(Decimal(egresos.valor_base) * Decimal(1.00), 2)
                            cursor.execute(
                                "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                    asiento.id,
                                    rubro.ctadebe_id,
                                    detalle,
                                    True,
                                    divisaid,
                                    Decimal(1.00),
                                    valor_base,
                                    valor_base,
                                    request.user.username,
                                    sucursalid,
                                    ''
                                ))
                            total_debe += valor_base

                        total_debe = math.ceil(total_debe * 100) / 100
                        total_haber = math.ceil(total_haber * 100) / 100

                        if total_debe != total_haber:
                            raise Exception(
                                'Asiento desbalanceado para el EGRESO de Inventario. TOTAL DEBE:{}  TOTAL HABER:{}'.format(
                                    total_debe, total_haber))

                    if lista_ingresos:

                        asientoid = get_contador_sucdiv(
                            'ACC_ASIENTOS-ID-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )
                        asiento_numero = get_contador_sucdiv(
                            'ACC_ASIENTOS-NUMBER-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )

                        ingresos_id = get_contador_sucdiv(
                            'INV_INGRESOS-ID-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )
                        ingresos_numero = get_contador_sucdiv(
                            'INV_INGRESOS-NUMBER-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )

                        ingresos = InvIngresos(
                            id=ingresos_id,
                            numero=ingresos_numero,
                            asientoid=asientoid,
                            bodega_id=fisico.bodega.id,
                            bodega_num=fisico.bodega.codigo,
                            division_id=divisionid,
                            fecha=fecha,
                            tipo='INV-IN',
                            detalle=detalle,
                            sucursalid=sucursalid
                        )
                        ingresos.save()

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

                        for item in lista_ingresos:
                            cantidad = abs(Decimal(item['cantidad']))
                            if cantidad != 0:

                                ingresos_dt_id = get_contador_sucdiv(
                                    'INV_INGRESOS_DT-ID-',
                                    '{}{}'.format(sucursalid, divisionid[-1])
                                )

                                producto = InvProductos.objects.get(pk=item['productoid'])
                                ingresos_detalle = InvIngresosProductos(
                                    id=ingresos_dt_id,
                                    ingreso_id=ingresos.id,
                                    bodega_id=fisico.bodega_id,
                                    cta_mayor_id=producto.ctamayor.id,
                                    producto_id=producto.id,
                                    cantidad=cantidad,
                                    empaque=item['empaque'],
                                    costo=producto.costo_promedio,
                                    factor=item['factor'],
                                    sucursalid=sucursalid,
                                    divisaid=divisaid,
                                    cambio=1
                                )
                                ingresos_detalle.save()

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
                                    total_unidades=round(cantidad * Decimal(item['factor'] * producto.costo_promedio ), 2),
                                    diferencia=item['diferencia'],
                                    sucursalid=sucursalid,
                                    ingreso=True,
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
                                        "{CALL INV_ProductosCardex_Insert_Conteo(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                        (
                                            producto.id,
                                            ingresos.bodega_id,
                                            asientoid,
                                            ingresos.id,
                                            ingresos.numero,
                                            fecha,
                                            ingresos.tipo,
                                            detalle,
                                            False,
                                            round(ingresos_detalle.cantidad * ingresos_detalle.factor, 2),
                                            ingresos_detalle.costo,
                                            divisaid,
                                            1,
                                            divisionid,
                                            request.user.username,
                                            sucursalid,
                                            ''
                                        ))

                        ingresos.valor_base = round(ingresos.invingresosproductos_set.aggregate(
                            valor=Coalesce(Sum(F('cantidad') * F('factor') * F('costo')), 0)
                        )['valor'],4)
                        ingresos.save()

                        total_debe = Decimal(0.00)
                        total_haber = Decimal(0.00)

                        rubro = InvRubros.objects.get(anulado=False, codigo='ING-007')

                        with connection.cursor() as cursor:
                            cursor.execute(
                                "{CALL INV_IngresosRubros_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                (
                                    ingresos.id,
                                    rubro.id,
                                    detalle,
                                    rubro.ctahaber_id,
                                    divisaid,
                                    Decimal('1.00'),
                                    round(Decimal(ingresos.valor_base) * Decimal(1.00), 4),
                                    False,
                                    request.user.username,
                                    sucursalid,
                                    ''
                                ))

                        asiento = AccAsientos(
                            id=asientoid,
                            numero=asiento_numero,
                            documentoid=ingresos.id,
                            fecha=fecha,
                            tipo=ingresos.tipo,
                            detalle=detalle,
                            divisionid=divisionid,
                            sucursalid=sucursalid
                        )
                        asiento.save()

                        ctas_mayor = ingresos.invingresosproductos_set.filter(cantidad__gt=0).values(
                            'cta_mayor_id'
                        ).annotate(
                            valor=Coalesce(Sum(F('cantidad') * F('factor') * F('costo')),0)
                        ).order_by('cta_mayor_id')

                        for cm in ctas_mayor:
                            if cm['valor'] > 0:
                                if cm['cta_mayor_id']:
                                    with connection.cursor() as cursor:
                                        valor_base = round(Decimal(cm['valor']) * Decimal(1.00), 4)
                                        cursor.execute(
                                            "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                                asiento.id,
                                                cm['cta_mayor_id'],
                                                detalle,
                                                True,
                                                divisaid,
                                                Decimal(1.00),
                                                valor_base,
                                                valor_base,
                                                request.user.username,
                                                sucursalid,
                                                ''
                                            ))
                                        total_debe += valor_base

                        with connection.cursor() as cursor:
                            valor_base = round(Decimal(ingresos.valor_base) * Decimal(1.00), 4)
                            cursor.execute(
                                "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                    asiento.id,
                                    rubro.ctahaber_id,
                                    detalle,
                                    False,
                                    divisaid,
                                    Decimal(1.00),
                                    valor_base,
                                    valor_base,
                                    request.user.username,
                                    sucursalid,
                                    ''
                                ))
                            total_haber+= valor_base

                        total_debe = math.ceil(total_debe * 100) / 100
                        total_haber = math.ceil(total_haber * 100) / 100
                        if total_debe != total_haber:
                            raise Exception(
                                'Asiento desbalanceado para el INGRESO de Inventario. TOTAL DEBE:{}  TOTAL HABER:{}'.format(total_debe, total_haber))

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
                toma_fisico = InvFisico.objects.get(pk=pk,anulado=False)
            except:
                raise Exception("No se econtro la toma fisica Id.")

            if toma_fisico.procesado:
                return redirect('/inventario/fisico/')

            if toma_fisico.bodega is None:
                raise Exception("No se encontro bodega..")

            # fisico_productos = toma_fisico.invfisicoproductos_set.filter(anulado=False, procesado=False)
            # productos = []
            # bodegaid = toma_fisico.bodega_id
            # sucursalid = toma_fisico.sucursalid
            #
            # for item in fisico_productos:
            #
            #     fisico_stock = round(item.cantidad, 2)
            #     stock_conversion = (item.stock / item.producto.conversion)
            #     fisico_conversion = (fisico_stock / item.producto.conversion)
            #
            #     productos.append({
            #         'producto': item.producto,
            #         'fisico_stock': fisico_stock,
            #         'fisico_cajas': int(fisico_conversion),
            #         'fisico_unidades': round((fisico_conversion % 1) * item.producto.conversion, 2),
            #         'stock': item.stock,
            #         'conversion': round(item.producto.conversion, 2),
            #         'stock_conversion': round(stock_conversion, 2),
            #         'cajas': int(stock_conversion),
            #         'unidades': round((stock_conversion % 1) * item.producto.conversion, 2),
            #         'diferencia': round(item.stock - fisico_stock, 2),
            #         'costo': item.producto.costo_promedio,
            #         'costo_total': abs(round((item.stock - fisico_stock) * item.producto.costo_promedio, 2))
            #     })

            fisico_productos = toma_fisico.invfisicoproductos_set.filter(anulado=False,procesado=False)\
                .values('producto_id')\
                .annotate(unds=Coalesce(Sum(F('cantidad') * F('factor')), 0))\
                .order_by('producto_id')

            productos = []
            bodegaid = toma_fisico.bodega_id
            sucursalid = toma_fisico.sucursalid

            for item in fisico_productos:
                producto = InvProductos.objects.get(pk=item['producto_id'])
                producto_stock = producto.get_bodega_stock_sistema(bodegaid,sucursalid)
                stock = Decimal('0.00')
                if producto_stock is None:
                    stock = Decimal('0.00')
                    # with connection.cursor() as cursor:
                    #     cursor.execute(
                    #         "{CALL Inv_ProductoBodega_Stock_Insert(%s,%s,%s)}", (
                    #             producto.id,
                    #             toma_fisico.bodega_id,
                    #             Decimal("0.00")
                    #         ))
                    #     stock = 0
                else:
                    stock = producto_stock['stock']

                fisico_stock = round(item['unds'],2)
                stock_conversion = (stock / producto.conversion)
                fisico_conversion = (fisico_stock / producto.conversion)

                productos.append({
                    'producto': producto,
                    'fisico_stock': fisico_stock,
                    'fisico_cajas': int(fisico_conversion),
                    'fisico_unidades': round((fisico_conversion % 1) * producto.conversion,2),
                    'stock': stock,
                    'conversion': round(producto.conversion,2),
                    'stock_conversion': round(stock_conversion,2),
                    'cajas': int(stock_conversion),
                    'unidades': round((stock_conversion % 1) * producto.conversion,2),
                    #'diferencia': round(stock - fisico_stock,2),
                    'diferencia': round(fisico_stock,2),
                    'costo': producto.costo_promedio,
                    'costo_total': abs(round((stock - fisico_stock) * producto.costo_promedio, 2))
                })

            data['sucursal'] = SisSucursales.objects.get(codigo=toma_fisico.sucursalid)
            data['divisiones'] = SisDivisiones.objects.filter(anulado=False)
            data['bodegas_origen'] = InvBodegas.objects.filter(anulado=False,transferencia=True)
            data['bodegas_destino'] = InvBodegas.objects.filter(anulado=False)

            if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                data['disabled'] = True

            data['toma_fisico'] = toma_fisico
            data['productos_detalle'] = productos

            return render(request, 'inventario/inv_conteo_fisico.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')

class InvTomaFisicoNoExistente(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        try:
            accion = request.POST.get('accion')
            if accion == 'guardar-ingreso-egreso':

                with transaction.atomic():

                    json_data = json.loads(request.POST['toma_fisico'])
                    try:
                        fisico = InvFisico.objects.get(pk=json_data['id'])
                    except:
                        raise Exception("No se encontró toma fisico ID")

                    fecha = datetime.datetime.strptime(json_data['fecha'], '%d/%m/%Y')
                    sucursalid = fisico.sucursalid
                    divisionid = fisico.division_id
                    divisaid = DIVISA_ID
                    detalle = json_data['detalle'].strip()

                    lista_egresos = [item for item in json_data['items'] if Decimal(item['cantidad']) > 0]
                    lista_ingresos = [item for item in json_data['items'] if Decimal(item['cantidad']) < 0]

                    if lista_egresos:

                        asientoid = get_contador_sucdiv(
                            'ACC_ASIENTOS-ID-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )
                        asiento_numero = get_contador_sucdiv(
                            'ACC_ASIENTOS-NUMBER-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )

                        egresos_id = get_contador_sucdiv(
                            'INV_EGRESOS-ID-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )
                        egresos_numero = get_contador_sucdiv(
                            'INV_EGRESOS-NUMBER-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )

                        egresos = InvEgresos(
                            id=egresos_id,
                            numero=egresos_numero,
                            asientoid=asientoid,
                            bodega_id=fisico.bodega.id,
                            bodega_num=fisico.bodega.codigo,
                            division_id=divisionid,
                            fecha=fecha,
                            tipo='INV-EG',
                            detalle=detalle,
                            sucursalid=sucursalid
                        )
                        egresos.save()

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

                        for item in lista_egresos:
                            cantidad = abs(Decimal(item['cantidad']))
                            if cantidad != 0:

                                egresos_dt_id = get_contador_sucdiv(
                                    'INV_EGRESOS_DT-ID-',
                                    '{}{}'.format(sucursalid, divisionid[-1])
                                )
                                producto = InvProductos.objects.get(pk=item['productoid'])

                                egresos_detalle = InvEgresosProductos(
                                    id=egresos_dt_id,
                                    egreso_id=egresos.id,
                                    cta_mayor_id=producto.ctamayor.id,
                                    producto_id=producto.id,
                                    stock=item['stock'],
                                    cantidad=cantidad,
                                    empaque=item['empaque'],
                                    costo=producto.costo_promedio,
                                    factor=item['factor'],
                                    sucursalid=sucursalid
                                )
                                egresos_detalle.save()

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
                                    egreso=True,
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
                                        "{CALL INV_ProductosCardex_Insert_Conteo(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                        (
                                            producto.id,
                                            egresos.bodega_id,
                                            asientoid,
                                            egresos.id,
                                            egresos.numero,
                                            fecha,
                                            egresos.tipo,
                                            detalle,
                                            True,
                                            round(egresos_detalle.cantidad * egresos_detalle.factor, 2),
                                            egresos_detalle.costo,
                                            divisaid,
                                            1,
                                            divisionid,
                                            request.user.username,
                                            sucursalid,
                                            ''
                                        ))

                        egresos.valor_base = round(egresos.invegresosproductos_set.aggregate(
                            valor=Coalesce(Sum(F('cantidad') * F('factor') * F('costo')), 0)
                        )['valor'],2)
                        egresos.save()

                        total_debe = Decimal(0.00)
                        total_haber = Decimal(0.00)

                        rubro = InvRubros.objects.get(anulado=False, codigo='EGR-008')

                        with connection.cursor() as cursor:
                            cursor.execute(
                                "{CALL INV_EgresosRubros_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                (
                                    egresos.id,
                                    rubro.id,
                                    detalle,
                                    rubro.ctadebe_id,
                                    divisaid,
                                    Decimal('1.00'),
                                    round(egresos.valor_base * Decimal(1.00), 2),
                                    True,
                                    request.user.username,
                                    sucursalid,
                                    ''
                                ))

                        asiento = AccAsientos(
                            id=asientoid,
                            numero=asiento_numero,
                            documentoid=egresos.id,
                            fecha=fecha,
                            tipo=egresos.tipo,
                            detalle=detalle,
                            divisionid=divisionid,
                            sucursalid=sucursalid
                        )
                        asiento.save()

                        ctas_mayor = egresos.invegresosproductos_set.filter(cantidad__gt=0).values(
                            'cta_mayor_id'
                        ).annotate(
                            valor=Coalesce(Sum(F('cantidad') * F('factor') * F('costo')), 0)
                        ).order_by('cta_mayor_id')

                        for cm in ctas_mayor:
                            if cm['valor'] > 0:
                                if cm['cta_mayor_id']:
                                    with connection.cursor() as cursor:
                                        valor_base = round(Decimal(cm['valor']) * Decimal(1.00), 2)
                                        cursor.execute(
                                            "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                                asiento.id,
                                                cm['cta_mayor_id'],
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

                        with connection.cursor() as cursor:
                            valor_base = round(Decimal(egresos.valor_base) * Decimal(1.00), 2)
                            cursor.execute(
                                "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                    asiento.id,
                                    rubro.ctadebe_id,
                                    detalle,
                                    True,
                                    divisaid,
                                    Decimal(1.00),
                                    valor_base,
                                    valor_base,
                                    request.user.username,
                                    sucursalid,
                                    ''
                                ))
                            total_debe += valor_base

                        total_debe = math.ceil(total_debe * 100) / 100
                        total_haber = math.ceil(total_haber * 100) / 100

                        if total_debe != total_haber:
                            raise Exception(
                                'Asiento desbalanceado para el EGRESO de Inventario. TOTAL DEBE:{}  TOTAL HABER:{}'.format(
                                    total_debe, total_haber))

                    if lista_ingresos:

                        asientoid = get_contador_sucdiv(
                            'ACC_ASIENTOS-ID-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )
                        asiento_numero = get_contador_sucdiv(
                            'ACC_ASIENTOS-NUMBER-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )

                        ingresos_id = get_contador_sucdiv(
                            'INV_INGRESOS-ID-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )
                        ingresos_numero = get_contador_sucdiv(
                            'INV_INGRESOS-NUMBER-',
                            '{}{}'.format(sucursalid, divisionid[-1])
                        )

                        ingresos = InvIngresos(
                            id=ingresos_id,
                            numero=ingresos_numero,
                            asientoid=asientoid,
                            bodega_id=fisico.bodega.id,
                            bodega_num=fisico.bodega.codigo,
                            division_id=divisionid,
                            fecha=fecha,
                            tipo='INV-IN',
                            detalle=detalle,
                            sucursalid=sucursalid
                        )
                        ingresos.save()

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

                        for item in lista_ingresos:
                            cantidad = abs(Decimal(item['cantidad']))
                            if cantidad != 0:

                                ingresos_dt_id = get_contador_sucdiv(
                                    'INV_INGRESOS_DT-ID-',
                                    '{}{}'.format(sucursalid, divisionid[-1])
                                )

                                producto = InvProductos.objects.get(pk=item['productoid'])
                                ingresos_detalle = InvIngresosProductos(
                                    id=ingresos_dt_id,
                                    ingreso_id=ingresos.id,
                                    bodega_id=fisico.bodega_id,
                                    cta_mayor_id=producto.ctamayor.id,
                                    producto_id=producto.id,
                                    cantidad=cantidad,
                                    empaque=item['empaque'],
                                    costo=producto.costo_promedio,
                                    factor=item['factor'],
                                    sucursalid=sucursalid,
                                    divisaid=divisaid,
                                    cambio=1
                                )
                                ingresos_detalle.save()

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
                                    ingreso=True,
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
                                        "{CALL INV_ProductosCardex_Insert_Conteo(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                        (
                                            producto.id,
                                            ingresos.bodega_id,
                                            asientoid,
                                            ingresos.id,
                                            ingresos.numero,
                                            fecha,
                                            ingresos.tipo,
                                            detalle,
                                            False,
                                            round(ingresos_detalle.cantidad * ingresos_detalle.factor, 2),
                                            ingresos_detalle.costo,
                                            divisaid,
                                            1,
                                            divisionid,
                                            request.user.username,
                                            sucursalid,
                                            ''
                                        ))

                        ingresos.valor_base = round(ingresos.invingresosproductos_set.aggregate(
                            valor=Coalesce(Sum(F('cantidad') * F('factor') * F('costo')), 0)
                        )['valor'],2)
                        ingresos.save()

                        total_debe = Decimal(0.00)
                        total_haber = Decimal(0.00)

                        rubro = InvRubros.objects.get(anulado=False, codigo='ING-007')

                        with connection.cursor() as cursor:
                            cursor.execute(
                                "{CALL INV_IngresosRubros_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                (
                                    ingresos.id,
                                    rubro.id,
                                    detalle,
                                    rubro.ctahaber_id,
                                    divisaid,
                                    Decimal('1.00'),
                                    round(Decimal(ingresos.valor_base) * Decimal(1.00), 2),
                                    False,
                                    request.user.username,
                                    sucursalid,
                                    ''
                                ))

                        asiento = AccAsientos(
                            id=asientoid,
                            numero=asiento_numero,
                            documentoid=ingresos.id,
                            fecha=fecha,
                            tipo=ingresos.tipo,
                            detalle=detalle,
                            divisionid=divisionid,
                            sucursalid=sucursalid
                        )
                        asiento.save()

                        ctas_mayor = ingresos.invingresosproductos_set.filter(cantidad__gt=0).values(
                            'cta_mayor_id'
                        ).annotate(
                            valor=Coalesce(Sum(F('cantidad') * F('factor') * F('costo')),0)
                        ).order_by('cta_mayor_id')

                        for cm in ctas_mayor:
                            if cm['valor'] > 0:
                                if cm['cta_mayor_id']:
                                    with connection.cursor() as cursor:
                                        valor_base = round(Decimal(cm['valor']) * Decimal(1.00), 2)
                                        cursor.execute(
                                            "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                                asiento.id,
                                                cm['cta_mayor_id'],
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

                        with connection.cursor() as cursor:
                            valor_base = round(Decimal(ingresos.valor_base) * Decimal(1.00), 2)
                            cursor.execute(
                                "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                    asiento.id,
                                    rubro.ctahaber_id,
                                    detalle,
                                    False,
                                    divisaid,
                                    Decimal(1.00),
                                    valor_base,
                                    valor_base,
                                    request.user.username,
                                    sucursalid,
                                    ''
                                ))
                            total_haber+= valor_base

                        total_debe = math.ceil(total_debe * 100) / 100
                        total_haber = math.ceil(total_haber * 100) / 100
                        if total_debe != total_haber:
                            raise Exception(
                                'Asiento desbalanceado para el INGRESO de Inventario. TOTAL DEBE:{}  TOTAL HABER:{}'.format(total_debe, total_haber))

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
                toma_fisico = InvFisico.objects.get(pk=pk,anulado=False)
            except:
                raise Exception("No se econtro la toma fisica Id.")

            if toma_fisico.bodega is None:
                raise Exception("No se encontro bodega..")

            # fisico_productos = toma_fisico.invfisicoproductos_set.filter(anulado=False) \
            #     .values_list('producto_id',flat=True) \
            #     .annotate(cant=Count('producto_id')) \
            #     .order_by('producto_id')
            #
            # producto_bodegas = InvPdBodegaStock.objects.filter(
            #     bodega_id=toma_fisico.bodega_id,
            # ).exclude(
            #     producto_id__in=list(fisico_productos)
            # ).exclude(
            #     stock=0
            # )

            producto_bodegas = InvPdBodegaStock.objects.filter(
                    bodega_id=toma_fisico.bodega_id,
                    ajustado=False
                ).exclude(
                    stock=0
                )

            data['sucursal'] = SisSucursales.objects.get(codigo=toma_fisico.sucursalid)
            data['divisiones'] = SisDivisiones.objects.filter(anulado=False)
            data['bodegas_origen'] = InvBodegas.objects.filter(anulado=False, transferencia=True)
            data['bodegas_destino'] = InvBodegas.objects.filter(anulado=False)

            if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                data['disabled'] = True

            data['toma_fisico'] = toma_fisico
            data['productos_detalle'] = producto_bodegas

            return render(request, 'inventario/inv_conteo_fisico_no_existencia.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def inv_toma_fisica_crear(request,template_name='inventario/inv_toma_fisico_crear.html'):
    if request.method == 'POST':
        form = InvTomaFisicoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/inventario/fisico/')
    else:
        form = InvTomaFisicoForm()

    data = {'accion': 'Crear'}
    addUserData(request, data)
    data['form'] = form
    return render(request, template_name, data)

def inv_get_detalle_toma_fisica(request):
    data = {'resp': False, 'error': ''}
    if request.method == 'GET':
        try:
            accion = request.GET.get('accion', '')

            if accion == 'detalle-toma-fisica':
                try:
                    toma_fisico = InvFisico.objects.get(pk=request.GET['id'], anulado=False)
                except:
                    raise Exception("No se econtro la toma fisica Id.")

                productos = []

                conteo_detalle = InvConteoDt.objects.filter(anulado=False, conteo__toma_fisica=toma_fisico).order_by('producto__codigo')

                for item in conteo_detalle:
                    stock_sistema = item.producto.get_bodega_stock_sistema(toma_fisico.bodega.id, toma_fisico.sucursalid)['stock']
                    productos.append({
                        'codigo' : item.producto.codigo,
                        'producto': item.producto.nombre,
                        'formato' : item.producto.descripcion,
                        'fisico_stock': item.cantidad,
                        'stock': stock_sistema,
                        'conversion': round(item.producto.conversion, 2),
                        'diferencia': round(stock_sistema - item.cantidad, 2),
                        'procesado': item.procesado ,
                        'transferencia': item.transferencia,
                        'ajuste': item.ajuste,
                        'total_unidades': item.total_unidades
                    })

                data['productos_detalle'] = productos
                data['toma_fisica'] = {
                    "id":toma_fisico.id,
                    "detalle":toma_fisico.detalle,
                    "bodega":toma_fisico.bodega.nombre,
                    "estado":toma_fisico.estado
                }
                data['resp'] = True
                return JsonResponse(data, status=200)

        except Exception as e:
            data['error'] = str(e)
    return JsonResponse(data, status=200)
