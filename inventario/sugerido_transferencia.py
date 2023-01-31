import datetime
import json
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, F, Count
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from inventario.models import InvBodegas, InvProductos, InvProductosEmpaques, InvTransferencias, InvTransferenciasDt
from sistema.funciones import addUserData
from sistema.models import SisSucursales, SisParametros
from venta.models import VenFacturasDetalle
from django.db import transaction
from contadores.fn_contador import get_contador_sucdiv

class InvSugeridoTransferencia(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        accion = request.POST['accion']
        try:
            if accion == 'inv-transferencia-sugerido':
                try:

                    bodega_origen_id = self.request.POST.get('bodega_origen_id', '')
                    sucursal_id = self.request.POST.get('sucursal_id', '')
                    producto_id = self.request.POST.get('producto_id', '')
                    promedio_venta_id = self.request.POST.get('promedio_venta_id',5)
                    con_dias = self.request.POST.get('con_dias', None)

                    if not bodega_origen_id:
                        raise Exception("Debe seleccionar una bodega de origen para generar el sugerido de transferencia")

                    if not sucursal_id:
                        raise Exception("Debe seleccionar una sucursal para generar el sugerido de transferencia")

                    try:
                        bodega_origen = InvBodegas.objects.filter(id=bodega_origen_id).first()
                    except:
                        raise Exception("No se encontró la bodega de origen")

                    try:
                        bodega_destino = InvBodegas.objects.filter(sucursal=sucursal_id).first()
                    except:
                        raise Exception("No se encontró la bodega de destino")

                    dias = int(self.request.POST.get('dias', 0))

                    final = datetime.datetime.now().date()
                    if con_dias is None:
                        inicio = datetime.datetime.now().date()
                    else:
                        if dias <= 0:
                            dias = 1
                        inicio = (final - datetime.timedelta(days=dias))

                    try:
                        date_range = (
                            datetime.datetime.combine(inicio, datetime.datetime.min.time()),
                            datetime.datetime.combine(final, datetime.datetime.max.time())
                        )

                        criterio_ventas = {
                            'factura__fecha__range': date_range,
                            'sucursalid' : sucursal_id
                        }

                        valor_ventas_dias = abs((final - inicio).days)

                    except:
                        criterio_ventas = {}
                        valor_ventas_dias = 0


                    criterio_productos = {
                        'id': producto_id,
                        'invpdbodegastock__bodega_id': bodega_origen_id
                    }

                    if bodega_origen_id:
                        criterio_productos['invpdbodegastock__bodega__venta'] = True

                    def queries(filters):
                        return [Q(**{k: v}) for k, v in filters.items() if v]

                    if producto_id:
                        sugerido_productos = InvProductos.objects.filter(Q(anulado=False),Q(vendible=True), *queries(criterio_productos)).values('id')
                    else:
                        if not VenFacturasDetalle.objects.filter(factura__anulado=False,*queries(criterio_ventas)).exists():
                            raise Exception("Asegúrese que las ventas se encuentren en el rango de las fechas indicadas")

                        sugerido_productos = VenFacturasDetalle.objects.filter(
                            factura__anulado=False,
                            *queries(criterio_ventas)
                        ).values(
                                'producto__id', 'bodega_id', "bodega__sucursal"
                            ).annotate(
                                cantidad=Count('producto__id')
                            ).order_by(
                                'producto__nombre'
                            )

                    lista_sugeridos = []

                    sugerido = Decimal('0.00')
                    cantidad = Decimal('0.00')
                    numero_ventas = Decimal('0.00')
                    ventas_dias = valor_ventas_dias
                    stock = Decimal('0.00')
                    stock_origen = Decimal('0.00')

                    parametro = SisParametros.objects.get(codigo='IMPUESTO-IVA-COMPRA')
                    tasa_impuesto = (Decimal(parametro.valor.strip()) / 100)

                    for p in sugerido_productos:

                        if not producto_id:
                            productoId = p['producto__id']
                            numero_ventas = p['cantidad']
                        else:
                            productoId = p['id']

                        producto = InvProductos.objects.filter(id=productoId).first()

                        total_unidades = producto.venfacturasdetalle_set.filter(*queries(criterio_ventas))\
                            .aggregate(total_unidades=Coalesce(Sum(F('cantidad') - F('devuelto')), 0))['total_unidades']

                        if total_unidades is None:
                            total_unidades = Decimal('1.00')

                        try:
                            if numero_ventas > 0 and ventas_dias > 0:
                                promedio_ventas = round(total_unidades / ventas_dias, 2)
                            else:
                                promedio_ventas = round(total_unidades / 1, 2)
                        except:
                            promedio_ventas = 0

                        if promedio_ventas >= int(promedio_venta_id) or producto_id:

                            stock_sucursal = producto.get_bodega_stock(bodega_destino.id, bodega_destino.sucursal)

                            stock_origen_bod = producto.get_bodega_stock(bodega_origen.id, bodega_origen.sucursal)

                            if stock_sucursal is not None:
                                stock = stock_sucursal['stock']

                            if stock_origen_bod is not None:
                                stock_origen = stock_origen_bod['stock']

                            conversion = Decimal(producto.conversion)
                            stock_conversion = stock / conversion

                            impuesto_id = str(producto.impuesto_compraid).strip()

                            if impuesto_id:
                                costo_compra = round(Decimal(producto.costo_promedio) * (1 + tasa_impuesto), 4)
                            else:
                                costo_compra = producto.costo_promedio

                            costo_caja = round(costo_compra * producto.conversion, 2)

                            e = None
                            if round(total_unidades, 2) >= conversion:
                                cantidad = round(total_unidades / conversion)
                                sugerido = cantidad * conversion
                                e = InvProductosEmpaques.objects.filter(
                                    producto_id=productoId,
                                    codigo='C'
                                ).exclude(codigo='N').exclude(codigo_barra='').first()

                            if e is None:
                                cantidad = round(total_unidades) if total_unidades > 0 else Decimal('1.00')
                                sugerido = cantidad
                                e = InvProductosEmpaques.objects.filter(
                                    producto_id=productoId
                                ).exclude(codigo__in=('C', 'N')).exclude(codigo_barra='').first()

                            total_costo = round(sugerido * costo_compra, 2)

                            lista_sugeridos.append({
                                'producto_id': producto.id,
                                'codigo': producto.codigo,
                                'nombre': producto.nombre,
                                'presentacion': producto.descripcion,
                                'costo': costo_compra,
                                'costo_caja': costo_caja,
                                'conversion': round(conversion, 2),
                                'balanza': producto.balanza,
                                'cajas': int(stock_conversion),
                                'stock': round(stock, 2),
                                'stock_borigen': round(stock_origen, 2),
                                'ventas': numero_ventas,
                                'promedio_ventas': promedio_ventas,
                                'cantidad': cantidad,
                                'sugerido': round(sugerido, 2),
                                'total' : total_costo,
                                'unidades' : round(total_unidades, 2),
                                'empaque': e.nombre.lower().strip(),
                                'empaque_id': str(e.codigo_barra).strip(),
                                'empaque_codigo': str(e.codigo).strip(),
                                'factor': round(e.factor, 2),
                                'procesar': False
                            })
                    data['productos_sugeridos'] = lista_sugeridos
                    data['resp'] = True

                    return JsonResponse(data, status=200)
                except Exception as e:
                    data['error'] = str(e)


            elif accion == 'generar-transferencia':
                with transaction.atomic():
                    try:
                        json_data = json.loads(request.POST['transferencia'])

                        try:
                            inventario = self.request.user.segusuarioparametro.inventario
                            if inventario is None:
                                raise
                        except:
                            raise Exception("Invalido paramatros bodega destino..")

                        fecha = datetime.date.today()
                        divisionid = inventario.division.id
                        sucursal = SisSucursales.objects.get(codigo=json_data['sucursal_id'])
                        bodega_destino = InvBodegas.objects.filter(sucursal=sucursal.codigo).first()
                        bodega_origen = InvBodegas.objects.get(id=json_data['bodega_origen_id'])

                        tranferencia_id = get_contador_sucdiv('INV_TRANSFERENCIAS-ID-','{}{}'.format(sucursal.codigo, divisionid[-1]))
                        tranferencia_numero = get_contador_sucdiv('INV_TRANSFERENCIAS-NUMBER-','{}{}'.format(sucursal.codigo, divisionid[-1]))

                        tranferencia = InvTransferencias(
                            id=tranferencia_id,
                            numero=tranferencia_numero,
                            division_id=divisionid,
                            fecha=fecha,
                            tipo='INV-TRS',
                            bodega_origen_id=bodega_origen.id,
                            bodega_destino_id=bodega_destino.id,
                            bodega_numero_origen=bodega_origen.codigo,
                            bodega_numero_destino=bodega_destino.codigo,
                            procesado=False,
                            detalle='TRANSFERENCIA REALIZADA DESDE UN SUGERIDO'
                        )
                        tranferencia.save()

                        for item in json_data['items']:
                            cantidad = Decimal(item['cantidad'])
                            factor = Decimal(item['factor'])
                            if cantidad > 0 and item['procesar']:
                                tranferenci_dt_id = get_contador_sucdiv('INV_TRANSFERENCIAS_DT-ID-','{}{}'.format(sucursal.codigo, divisionid[-1]))
                                producto = InvProductos.objects.get(pk=item['producto_id'])
                                tranferencia_detalle = InvTransferenciasDt(
                                    id=tranferenci_dt_id,
                                    transferencia_id=tranferencia.id,
                                    producto_id=producto.id,
                                    cantidad=cantidad,
                                    empaque=item['empaque'],
                                    costo=producto.costo_promedio,
                                    factor=factor,
                                    total=round(cantidad * factor * producto.costo_promedio, 2),
                                    sucursalid=sucursal.codigo
                                )
                                tranferencia_detalle.save()

                        tranferencia.total = round(
                            tranferencia.invtransferenciasdt_set.aggregate(costo_total=Coalesce(Sum('total'), 0))[
                                'costo_total'], 2)
                        tranferencia.save()
                        data['resp'] = True
                        return JsonResponse(data, status=200)

                    except Exception as e:
                        messages.add_message(request, 40, str(e))

        except Exception as e:
            messages.add_message(request, 40, str(e))
        return JsonResponse(data, status=200)

    def get(self, request, *args, **kwargs):
        data = {"editar":False}
        addUserData(request, data)
        try:
            data['sucursales'] = SisSucursales.objects.filter(anulado=False)
            data['bodegas'] = InvBodegas.objects.filter(anulado=False,transferencia=True)
            data['fecha'] = datetime.datetime.now()
            try:
                promedio_ventas = []
                for n in range(1,101):
                    promedio_ventas.append(n)
                data['promedios'] = promedio_ventas

            except:
                pass
            if request.user.is_superuser:
                return render(request, 'inventario/inv_sugerido_transferencia_admin.html', data)
            else:
                return render(request, 'inventario/inv_sugerido_tranferencia.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')