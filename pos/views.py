import datetime
import json
import math
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction, connection
from django.db.models import Sum, F, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.generic.base import View

from cliente.models import CliRubros
from contabilidad.models import AccAsientos
from contadores.fn_contador import get_contador_sucdiv
from empleado.models import EmpEmpleados
from pedido.models import VenOrdenPedidos
from sistema.constantes import ESTADO_ORDEN_PEDIDO, PEDIDOS_CONTROLA_STOCK, USER_ALL_PERMISOS
from sistema.funciones import addUserData
from sistema.models import SisParametros, SisDivisiones, SisSucursales
from venta.models import VenFacturas, VenFacturasDetalle, VenLiquidacionMovimientos

class InformeFacturarPedidosView(LoginRequiredMixin, ListView):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    model = VenOrdenPedidos
    template_name = 'pos/pos_informe_pedidos.html'
    context_object_name = 'ordenes'
    paginate_by = 20
    creadopor = ''
    disabled = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        addUserData(self.request, context)
        qs = kwargs.pop('ordenes', self.object_list)
        context['total'] = 0.00

        total = qs.aggregate(total=Sum('total'))['total']
        if total is not None:
            context['total'] = total

        s = self.request.GET.get('s', '')
        divisionid = self.request.GET.get('divisionid', '')
        vendedorid = self.request.GET.get('vendedorid', '')
        estado_pedido = self.request.GET.get('estado_pedido', '')

        inicio = self.request.GET.get('inicio', '')
        final = self.request.GET.get('final', '')

        url = '&s={}&inicio={}&final={}&divisionid={}&vendedorid={}&creadopor={}&estado_pedido={}'.format(
            s, inicio, final, divisionid, vendedorid, self.creadopor, estado_pedido
        )
        context['url'] = url
        context['s'] = s
        context['inicio'] = inicio
        context['final'] = final
        context['divisionid'] = divisionid
        context['vendedorid'] = vendedorid
        context['creadopor'] = self.creadopor
        context['disabled'] = self.disabled
        context['estado_pedido'] = estado_pedido

        context['divisiones'] = SisDivisiones.objects.all()
        context['usuarios'] = User.objects.filter(is_active=True)
        context['vendedores'] = EmpEmpleados.objects.filter(anulado=False, vendedor=True)
        context['estado_pedidos'] = ESTADO_ORDEN_PEDIDO

        return context

    def get_queryset(self, **kwargs):
        search = self.request.GET.get('s', '')
        criterio = {
            'division_id': self.request.GET.get('divisionid', ''),
            'vendedor_id': self.request.GET.get('vendedorid', ''),
            'creadopor': self.request.GET.get('creadopor', ''),
            'estado': self.request.GET.get('estado_pedido', '')
        }
        # if not self.request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
        #     criterio['creadopor'] = self.request.user.username
        #     self.disabled = True

        self.creadopor = criterio['creadopor']
        inicio = self.request.GET.get('inicio', '')
        final = self.request.GET.get('final', '')

        try:
            inicio = datetime.datetime.strptime(inicio, '%Y-%m-%d').date() if inicio else datetime.date.today()
            final = datetime.datetime.strptime(final, '%Y-%m-%d').date() if final else datetime.date.today()
            date_range = (
                datetime.datetime.combine(inicio, datetime.datetime.min.time()),
                datetime.datetime.combine(final, datetime.datetime.max.time())
            )
            criterio['fecha__range'] = date_range
        except:
            pass

        def queries(filters):
            return [Q(**{k: v}) for k, v in filters.items() if v]

        return VenOrdenPedidos.objects.filter(
            Q(anulado=False),
            Q(numero__icontains=search) |
            Q(ruc__icontains=search) |
            Q(cliente__nombre__icontains=search),
            *queries(criterio)
        )

class PosFacturarPedidoVenta(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        try:
            accion = request.POST.get('accion')
            if accion == 'pedido_procesar_factura':

                with transaction.atomic():
                    json_data = json.loads(request.POST['pedido'])
                    pedidoid = request.POST.get('pedidoid')
                    try:
                        pedido = VenOrdenPedidos.objects.get(pk=pedidoid)
                        if not '2' in pedido.estado:
                            raise Exception('No permite facturar el pedido.')

                    except:
                        raise Exception('No se encontró orden de pedido.')

                    total_debe = Decimal(0.00)
                    total_haber = Decimal(0.00)
                    tipo = 'VEN-FA'

                    sucursalid = pedido.sucursalid
                    divisionid = pedido.division_id
                    divisaid = pedido.divisaid

                    facturaid = get_contador_sucdiv('VEN_FACTURAS-ID-', '{}{}'.format(sucursalid, divisionid[-1]))
                    asientoid = get_contador_sucdiv('ACC_ASIENTOS-ID-', '{}{}'.format(sucursalid, divisionid[-1]))
                    asiento_numero = get_contador_sucdiv('ACC_ASIENTOS-NUMBER-','{}{}'.format(sucursalid, divisionid[-1]))

                    cliente = pedido.cliente
                    fecha = datetime.datetime.strptime(request.POST['fecha'], '%d/%m/%Y')
                    factura = VenFacturas(
                        id=facturaid,
                        ordenid=pedido.numero,
                        numero=facturaid,
                        secuencia=facturaid,
                        asientoid=asientoid,
                        cliente_id=pedido.cliente_id,
                        detalle=pedido.detalle,
                        ruc=pedido.ruc,
                        vendedorid=pedido.vendedor_id,
                        caja_id=pedido.caja_id,
                        terminoid=pedido.terminoid,
                        division_id=divisionid,
                        bodega_id=pedido.bodega_id,
                        contado=pedido.contado,
                        fecha=fecha,
                        entregado=pedido.entregado,
                        tipo=tipo,
                        divisaid=divisaid,
                        cambio=Decimal("1.00"),
                        subtotal=pedido.subtotal,
                        descuento=pedido.descuento,
                        impuesto=pedido.impuesto,
                        total=pedido.total,
                        total_comision=pedido.total_comision,
                        efectivo=Decimal("0.00"),
                        credito=pedido.total,
                        cupones=Decimal("0.00"),
                        fecha_cheque=fecha,
                        vence=fecha,
                        fecha_oc=datetime.datetime.strptime('01/01/1900', '%d/%m/%Y'),
                        forma_pago='CRE',
                        zona_id=cliente.zona_id,
                        holgura=Decimal(2.00),
                        nocontrola_stock=True,
                        reimpreso=True,
                        nota=pedido.nota,
                        sucursalid=sucursalid,
                        ptg_iva=Decimal(12.00),
                        subtotal_cero=pedido.subtotal_cero,
                        subtotal_iva=pedido.subtotal_iva,
                        archivo_sri=True
                    )
                    factura.save()

                    detalle = '{} Fact#:{}'.format(cliente.nombre, factura.id)

                    for item in pedido.venordenpedidosdetalle_set.filter(aprobado=True):
                        if item.cantidad > 0:

                            detalleid = get_contador_sucdiv('VEN_FACTURAS_DT-ID-','{}{}'.format(sucursalid, divisionid[-1]))
                            factura_detalle = VenFacturasDetalle(
                                id=detalleid,
                                factura_id=factura.id,
                                producto_id=item.producto_id,
                                bodega_id=item.bodega_id,
                                cantidad=round(item.cantidad * item.factor,2),
                                precio=item.precio,
                                costo=item.costo,
                                subtotal=item.subtotal,
                                tasa_descuento=item.tasa_descuento,
                                descuento=item.descuento,
                                tasa_impuesto=item.tasa_impuesto,
                                impuesto=item.impuesto,
                                total=item.total,
                                empaque=item.empaque,
                                precio_name=item.empaque,
                                factor=item.factor,
                                sucursalid=sucursalid,
                                clase=item.clase,
                                valor_comision=item.valor_comision
                            )
                            factura_detalle.save()

                            with connection.cursor() as cursor:
                                cursor.execute(
                                    "{CALL INV_ProductosCardex_Insert_WEB(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                    (
                                        item.producto_id,
                                        item.bodega_id,
                                        asientoid,
                                        factura.id,
                                        factura.id,
                                        fecha,
                                        tipo,
                                        detalle,
                                        True,
                                        round(item.cantidad * item.factor,2),
                                        item.costo,
                                        divisaid,
                                        1,
                                        divisionid,
                                        request.user.username,
                                        sucursalid,
                                        ''
                                    ))

                    asiento = AccAsientos(
                        id=asientoid,
                        numero=asiento_numero,
                        documentoid=factura.id,
                        fecha=fecha,
                        tipo=tipo,
                        detalle=detalle,
                        nota=cliente.nombre,
                        divisionid=divisionid,
                        sucursalid=sucursalid
                    )
                    asiento.save()

                    parametro = SisParametros.objects.get(codigo='CLI-RUBRO-FACTURA-ID')
                    rubro = CliRubros.objects.get(id=parametro.valor.strip())

                    # Asiento contable DEBE
                    valor_base = round(Decimal(factura.total) * Decimal(1.00), 4)
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                asiento.id,
                                rubro.ctadebe_id,
                                detalle,
                                True,
                                divisaid,
                                Decimal(1.00),
                                factura.total,
                                valor_base,
                                request.user.username,
                                sucursalid,
                                ''
                            ))

                    total_debe += valor_base
                    # Asiento cta. Descuentos Producto
                    cta_descuentos = factura.venfacturasdetalle_set.values(
                        ctadescuento=F('producto__ctadescuento')
                    ).annotate(
                        valor=Sum('descuento')
                    ).filter(cantidad__gt=0).exclude(clase='02').order_by('producto__ctadescuento')

                    for cd in cta_descuentos:
                        if cd['valor'] > 0:
                            if cd['ctadescuento']:
                                with connection.cursor() as cursor:
                                    valor_base = round(Decimal(cd['valor']) * Decimal(1.00), 4)
                                    cursor.execute(
                                        "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                            asiento.id,
                                            cd['ctadescuento'],
                                            detalle,
                                            True,
                                            divisaid,
                                            Decimal(1.00),
                                            Decimal(cd['valor']),
                                            valor_base,
                                            request.user.username,
                                            sucursalid,
                                            ''
                                        ))
                                    total_debe += valor_base

                    # Asiento cta. Costo Producto
                    cta_costos = factura.venfacturasdetalle_set.values(
                        ctacostos=F('producto__ctacostos'),
                    ).annotate(
                        valor=Sum(F('cantidad') * F('costo'))
                    ).filter(cantidad__gt=0).exclude(clase='02').order_by('producto__ctacostos')

                    for cc in cta_costos:
                        if cc['valor'] > 0:
                            if cc['ctacostos']:
                                with connection.cursor() as cursor:
                                    valor_base = round(Decimal(cc['valor']) * Decimal(1.00), 4)
                                    cursor.execute(
                                        "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                            asiento.id,
                                            cc['ctacostos'],
                                            detalle,
                                            True,
                                            divisaid,
                                            Decimal(1.00),
                                            cc['valor'],
                                            valor_base,
                                            request.user.username,
                                            sucursalid,
                                            ''
                                        ))
                                    total_debe += valor_base

                    # Asiento contable HABER
                    # cuenta mayor producto

                    cta_mayor = factura.venfacturasdetalle_set.values(
                        ctamayor=F('producto__ctamayor'),
                    ).annotate(
                        valor=Sum(F('cantidad') * F('costo'))
                    ).filter(cantidad__gt=0).exclude(clase='02').order_by('producto__ctamayor')

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

                    # cuenta ventas
                    cta_ventas = factura.venfacturasdetalle_set.values(
                        ctaventas=F('producto__ctaventas'),
                    ).annotate(
                        valor=Sum('subtotal')
                    ).filter(cantidad__gt=0).order_by('producto__ctaventas')

                    for cv in cta_ventas:
                        if cv['valor'] > 0:
                            if cv['ctaventas']:
                                with connection.cursor() as cursor:
                                    valor_base = round(Decimal(cv['valor']) * Decimal(1.00), 4)
                                    cursor.execute(
                                        "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                            asiento.id,
                                            cv['ctaventas'],
                                            detalle,
                                            False,
                                            divisaid,
                                            Decimal(1.00),
                                            Decimal(cv['valor']),
                                            valor_base,
                                            request.user.username,
                                            sucursalid,
                                            ''
                                        ))
                                    total_haber += valor_base

                    cta_impuestos = factura.venfacturasdetalle_set.values(
                        ctaimpuestos=F('producto__impuestoid')
                    ).annotate(
                        valor=Sum('impuesto')
                    ).filter(impuesto__gt=0).order_by('producto__impuestoid')

                    for ci in cta_impuestos:
                        if ci['valor'] > 0:
                            try:
                                paramatro = SisParametros.objects.get(id=ci['ctaimpuestos'])
                                cuentaid = paramatro.extradata.strip().replace('CuentaID=', '')
                            except:
                                raise Exception('No se encontró cuenta Iva.')

                            with connection.cursor() as cursor:
                                valor_base = round(Decimal(ci['valor']) * Decimal(1.00), 4)
                                cursor.execute(
                                    "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                    (
                                        asiento.id,
                                        cuentaid,
                                        detalle,
                                        False,
                                        divisaid,
                                        Decimal(1.00),
                                        Decimal(ci['valor']),
                                        valor_base,
                                        request.user.username,
                                        sucursalid,
                                        ''
                                    ))
                                total_haber += valor_base

                    total_debe = math.ceil(total_debe * 100) / 100
                    total_haber = math.ceil(total_haber * 100) / 100

                    if total_debe != total_haber:
                        raise Exception(
                            'Asiento desbalanceado. TOTAL DEBE:{}  TOTAL HABER:{}'.format(total_debe, total_haber))

                    cliente_deudaid = get_contador_sucdiv('CLI_CLIENTES_DEUDAS-ID-','{}{}'.format(sucursalid, divisionid[-1]))

                    with connection.cursor() as cursor:
                        valor_base = round(factura.total * Decimal(1.00), 2)
                        cursor.execute(
                            "{CALL CLI_ClientesDeudas_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                            (
                                cliente_deudaid,
                                factura.cliente_id,
                                factura.id,
                                asiento.id,
                                factura.id,
                                detalle,
                                round(factura.total, 2),
                                valor_base,
                                fecha,
                                fecha,
                                rubro.id,
                                rubro.ctadebe.id,
                                divisaid,
                                Decimal(1.00),
                                round(factura.total, 2),
                                tipo,
                                False,
                                '',
                                factura.vendedorid,
                                False,
                                divisionid,
                                request.user.username,
                                sucursalid,
                                '',
                                ''
                            ))

                    if factura.total_comision > 0:
                        movimiento = VenLiquidacionMovimientos(
                            fecha=factura.fecha,
                            vendedor_id=factura.vendedorid,
                            supervisorid=factura.entregadorid,
                            numcartilla=factura.numcartilla,
                            cliente_id=factura.cliente_id,
                            documentoid=factura.id,
                            contado=factura.contado,
                            numero=factura.numero,
                            detalle=factura.detalle,
                            valor_credito=factura.total,
                            valor=factura.total_comision,
                            valor_base=round(factura.total_comision * factura.cambio, 2),
                            divisaid=factura.divisaid,
                            cambio=factura.cambio,
                            saldo=factura.total_comision,
                            tipo=factura.tipo.strip(),
                            credito=False,
                            estado='3',
                            sucursalid=factura.sucursalid,
                            divisionid=factura.division_id
                        )
                        movimiento.save()
                    pedido.estado = '5'
                    pedido.procesado = True
                    pedido.save()
                    data['resp'] = True
                    return JsonResponse(data, status=200)
        except Exception as e:
            data['error'] = 'error: ' + str(e)
        return JsonResponse(data, status=200)

    def get(self, request, *args, **kwargs):
        data = {"procesar":False}
        addUserData(request, data)
        try:
            pedido_id = kwargs.get("pk", None)

            if pedido_id is not None:
                try:
                    pedido = VenOrdenPedidos.objects.get(pk=pedido_id,anulado=False)
                except:
                    raise Exception('No se encontro orden de pedido')

                data['fecha'] = pedido.fecha
                data['fecha_entrega'] = pedido.entregado

                caja = pedido.caja
                if caja is None:
                    raise Exception('No se encontro caja asociado al usuario..')

                try:
                    data['cliente'] = cliente = pedido.cliente
                    data['termino'] = termino = SisParametros.objects.get(pk=pedido.cliente.termino)
                    disponible = 0
                    saldo_total = 0

                    if termino.codigo != 'TER-CONTADO' and pedido.forma_pago == 'CRE':
                        try:
                            if cliente.empleadoid is not None and cliente.empleadoid.strip() != '':
                                empleado = EmpEmpleados.objects.get(pk=cliente.empleadoid)
                                saldo_total = cliente.get_saldo_total() + empleado.get_saldo_total_empleado()
                                disponible = cliente.cupo - saldo_total
                            else:
                                saldo_total = cliente.get_saldo_total()
                                disponible = cliente.cupo - saldo_total
                        except:
                            pass
                except:
                    data['cliente'] = None

                if caja.bodega is not None:
                    data['bodega'] = caja.bodega

                parametro = SisParametros.objects.get(codigo='IMPUESTO-IVA')
                data['tasa_impuesto'] = Decimal(parametro.valor.strip())
                data['cta_impuestoid'] = parametro.extradata.strip().replace('CuentaID=', '')
                data['controla_stock'] = PEDIDOS_CONTROLA_STOCK

                if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                    data['disabled'] = True

                data['caja'] = caja
                data['sucursal'] = SisSucursales.objects.get(codigo=caja.sucursal)
                data['pedido'] = pedido
                data['cupo'] = round(cliente.cupo,2)
                data['saldo_total'] = round(saldo_total,2)
                data['disponible'] = round(disponible,2)
                data['procesar'] = True

                return render(request, 'pos/pos_facturar_pedido.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/pos/factura/pedidos/')
