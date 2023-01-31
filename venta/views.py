import datetime
import json
import math
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection, transaction
from django.db.models import F, Sum, Count, Min, Q
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from cliente.models import CliRubros, CliClientesDeudas
from contabilidad.models import AccAsientos
from contadores.fn_contador import get_contador_sucdiv
from empleado.models import EmpEmpleados
from inventario.models import InvBodegas
from sistema.constantes import USER_ALL_PERMISOS, PORCENTAJE_COMISION, MINIMO_ABONO, MAXIMO_DIAS_CREDITO,ESTADO_COMISION
from sistema.funciones import addUserData
from sistema.models import SisSucursales, SisParametros
from venta.models import VenFacturas, VenFacturasDetalle, VenLiquidacionMovimientos, VenLiquidacionComision, \
    VenLiquidacionComisionDetalle, VenLiquidacionComisionTemporal, VenLiquidacionComisionDetalleTemporal

lista_cartillas_totales = ('886','885','890')
lista_cartillas_parcial = ('1057','1063')

class VenDocumentoFactura(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        accion = request.POST['accion']

        try:
            if accion == 'venta_factura_crear':

                with transaction.atomic():

                    json_data = json.loads(request.POST['factura'])
                    num_cartilla = json_data['numcartilla']

                    if VenFacturas.objects.filter(anulado=False, numcartilla=num_cartilla).exists():
                        raise Exception("Numero de cartilla ya existe")

                    total_debe = Decimal(0.00)
                    total_haber = Decimal(0.00)

                    sucursalid = json_data['sucursalid']
                    divisionid = json_data['divisionid']
                    divisaid = json_data['divisaid']
                    #tipo_modelo = json_data['tipo_modelo']

                    facturaid = get_contador_sucdiv('VEN_FACTURAS-ID-', '{}{}'.format(sucursalid, divisionid[-1]))
                    # factura_numero = get_contador_sucdiv('VEN_FACTURAS-NUMBER-','{}{}'.format(sucursalid,divisionid[-1]))
                    # secuencia = get_contador_sucdiv('VEN_FACTURAS-SECUENCIA-','{}{}'.format(sucursalid,divisionid[-1]))
                    asientoid = get_contador_sucdiv('ACC_ASIENTOS-ID-', '{}{}'.format(sucursalid, divisionid[-1]))
                    asiento_numero = get_contador_sucdiv('ACC_ASIENTOS-NUMBER-',
                                                         '{}{}'.format(sucursalid, divisionid[-1]))

                    cliente = json_data['cliente']

                    fecha = datetime.datetime.strptime(json_data['fecha'], '%d/%m/%Y')
                    factura = VenFacturas(
                        id=facturaid,
                        numero=facturaid,
                        secuencia=facturaid,
                        asientoid=asientoid,
                        cliente_id=json_data['clienteid'],
                        detalle=cliente['nombre'],
                        ruc=cliente['ruc'],
                        vendedorid=json_data['vendedorid'],
                        caja_id=json_data['cajaid'],
                        terminoid=json_data['terminoid'],
                        division_id=divisionid,
                        bodega_id=json_data['bodegaid'],
                        contado=json_data['contado'],
                        fecha=fecha,
                        entregado=fecha,
                        tipo=json_data['tipo'],
                        divisaid=divisaid,
                        cambio=Decimal(1.00),
                        subtotal=Decimal(json_data['subtotal']),
                        descuento=Decimal(json_data['descuento']),
                        impuesto=Decimal(json_data['impuesto']),
                        total=Decimal(json_data['total']),
                        total_comision=Decimal(json_data['total_comision']),
                        efectivo=Decimal(json_data['efectivo']),
                        credito=Decimal(json_data['credito']),
                        cupones=Decimal(json_data['cupones']),
                        fecha_cheque=fecha,
                        vence=fecha,
                        fecha_oc=datetime.datetime.strptime('01/01/1900', '%d/%m/%Y'),
                        forma_pago=json_data['formapago'],
                        verificadorid=json_data['verificadorid'],
                        recaudadorid=json_data['cobradorid'],
                        entregadorid=json_data['entregadorid'],
                        dia_cobro=json_data['diacobro'],
                        zona_id=json_data['zonaid'],
                        pagada=json_data['pagada'],
                        numcartilla=json_data['numcartilla'],
                        holgura=Decimal(2.00),
                        nocontrola_stock=False,
                        reimpreso=True,
                        nota=json_data['nota'],
                        sucursalid=sucursalid,
                        ptg_iva=Decimal(12.00),
                    )
                    factura.save()
                    detalle = '{} Fact#:{}'.format(cliente['nombre'], factura.id)

                    for item in json_data['items']:
                        if item['cantidad'] > 0:
                            detalleid = get_contador_sucdiv('VEN_FACTURAS_DT-ID-',
                                                            '{}{}'.format(sucursalid, divisionid[-1]))
                            factura_detalle = VenFacturasDetalle(
                                id=detalleid,
                                factura_id=factura.id,
                                producto_id=item['productoid'],
                                bodega_id=item['bodegaid'],
                                cantidad=item['cantidad'],
                                precio=item['precio'],
                                costo=item['costo'],
                                subtotal=item['subtotal'],
                                tasa_descuento=item['tasadescuento'],
                                descuento=item['descuento'],
                                tasa_impuesto=item['tasaimpuesto'],
                                impuesto=item['impuesto'],
                                total=item['total'],
                                empaque=item['empaque'],
                                precio_name=item['empaque'],
                                factor=item['factor'],
                                sucursalid=sucursalid,
                                clase=item['clase'],
                                valor_comision=item['valor_comision']
                            )
                            factura_detalle.save()

                            with connection.cursor() as cursor:
                                cursor.execute(
                                    "{CALL INV_ProductosCardex_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                    (
                                        item['productoid'],
                                        item['bodegaid'],
                                        asientoid,
                                        factura.id,
                                        factura.id,
                                        fecha,
                                        json_data['tipo'],
                                        detalle,
                                        True,
                                        item['cantidad'],
                                        item['costo'],
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
                        tipo=json_data['tipo'],
                        detalle=detalle,
                        nota=cliente['nombre'],
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
                                json_data['valor'],
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
                        # valor = round(Decimal(cc['cantidad']) * Decimal(cc['costo']), 2)
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
                        # valor = round(Decimal(cm['cantidad']) * Decimal(cm['costo']), 2)
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
                                raise Exception('No se encontro cuenta Iva.')

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

                    cliente_deudaid = get_contador_sucdiv('CLI_CLIENTES_DEUDAS-ID-',
                                                          '{}{}'.format(sucursalid, divisionid[-1]))

                    with connection.cursor() as cursor:
                        valor_base = round(factura.total * Decimal(1.00), 2)
                        cursor.execute(
                            "{CALL CLI_ClientesDeudas_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                            (
                                cliente_deudaid,
                                json_data['clienteid'],
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
                                json_data['tipo'],
                                False,
                                '',
                                json_data['vendedorid'],
                                False,
                                divisionid,
                                request.user.username,
                                sucursalid,
                                '',
                                factura.numcartilla.strip()
                            ))

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
                        divisionid=factura.division_id,
                        #tipo_modelo=tipo_modelo
                    )
                    movimiento.save()
                    data['resp'] = True
                    return JsonResponse(data, status=200)

        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, status=200)

    def get(self, request, *args, **kwargs):
        data = {}
        addUserData(request, data)
        try:
            caja = request.user.segusuarioparametro.caja
            if caja is None:
                raise Exception('No se encontro caja asociado al usuario..')

            data['caja_id'] = caja.id
            data['sucursal'] = SisSucursales.objects.get(codigo=caja.sucursal)
            data['bodegas'] = InvBodegas.objects.filter(anulado=False, sucursal=caja.sucursal)

            if caja.bodega is not None:
                data['bodega_id'] = caja.bodega.id

            if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                data['disabled'] = True
            return render(request, 'venta/ven_documento_factura.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')

class VenDocumentoFacturaCotizar(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        data = {}
        addUserData(request, data)
        try:
            caja = request.user.segusuarioparametro.caja
            if caja is None:
                raise Exception('No se encontro caja asociado al usuario..')

            data['caja_id'] = caja.id
            data['sucursal'] = SisSucursales.objects.get(codigo=caja.sucursal)
            data['bodegas'] = InvBodegas.objects.filter(anulado=False, sucursal=caja.sucursal)

            if caja.bodega is not None:
                data['bodega_id'] = caja.bodega.id

            if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                data['disabled'] = True
            return render(request, 'venta/ven_documento_factura_cotizar.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')

class VenComisionLiquidacionVentasrESPALDO(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        accion = request.POST['accion']

        try:
            x = 8

        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, status=200)

    def get(self, request, *args, **kwargs):
        data = {}
        addUserData(request, data)
        try:
            accion = request.GET.get('accion')

            fecha_corte = self.request.GET.get('fecha_corte', '')
            fecha_corte = datetime.datetime.strptime(fecha_corte,
                                                     '%Y-%m-%d').date() if fecha_corte else datetime.date.today()

            if accion == 'consultar':
                empleado = EmpEmpleados.objects.get(pk=request.GET.get('vendedorid'))
                deuda_cartillas = CliClientesDeudas.objects.filter(
                    anulado=False,
                    vendedorid=empleado.id,
                    fecha__lt=fecha_corte
                ).values(
                    'numcartilla', 'cliente_id', nombre=F('cliente__nombre')
                ).annotate(
                    fecha=Min('fecha')
                ).order_by('fecha', 'numcartilla', 'cliente__nombre')

                listado_deuda_cartillas = []
                total_debe = Decimal('0.0')
                total_haber = Decimal('0.0')
                total_saldo = Decimal('0.0')
                total_abono = Decimal('0.0')
                total_comision = Decimal('0.0')

                for dc in deuda_cartillas:
                    hoy = data['hoy']
                    try:
                        factura = VenFacturas.objects.get(numcartilla=dc['numcartilla'])
                        supervisor = EmpEmpleados.objects.get(pk=factura.entregadorid)
                        diferencia = hoy - factura.fecha
                    except:
                        factura = None
                        supervisor = None

                    debe = CliClientesDeudas.objects.filter(
                        anulado=False,
                        numcartilla=dc['numcartilla'],
                        cliente_id=dc['cliente_id'],
                        credito=False
                    ).aggregate(debe=Coalesce(Sum('valor'), 0))['debe']

                    total_debe += Decimal(debe)

                    pagos = CliClientesDeudas.objects.filter(
                        anulado=False,
                        numcartilla=dc['numcartilla'],
                        cliente_id=dc['cliente_id'],
                        credito=True
                    ).aggregate(haber=Coalesce(Sum('valor'), 0), cantidad=Count('valor'))

                    total_haber += Decimal(pagos['haber'])
                    saldo = round(Decimal(debe) - Decimal(pagos['haber']), 2)
                    total_saldo += saldo

                    total_abono += Decimal(pagos['cantidad'])

                    if saldo > 0:
                        comision = round(factura.total_comision / 2, 2)
                    else:
                        comision = factura.total_comision

                    total_comision += comision

                    item = {
                        'factura': factura,
                        'dias': diferencia.days,
                        'supervisor': supervisor,
                        'numcartilla': dc['numcartilla'],
                        'clienteid': dc['cliente_id'],
                        'nombre': dc['nombre'],
                        'debe': debe,
                        'haber': pagos['haber'],
                        'saldo': saldo,
                        'cantidad': pagos['cantidad'] if pagos['cantidad'] is not None else 0,
                        'comision': comision,
                    }
                    listado_deuda_cartillas.append(item)

                data['detalle_deudas'] = listado_deuda_cartillas
                data['total_debe'] = total_debe
                data['total_haber'] = total_haber
                data['total_saldo'] = total_saldo
                data['total_abono'] = total_abono
                data['total_comision'] = total_comision

                data['total_ventas'] = deuda_cartillas.count()
                data['empleado'] = empleado
                data['porcentaje_comision'] = PORCENTAJE_COMISION

            data['fecha_corte'] = fecha_corte
            return render(request, 'venta/ven_comision_liquidacion_ventas.html', data)

        except Exception as e:
            messages.add_message(request, 40, 'No se encontro ventas.')
        return redirect('/venta/comision/liquidacion/')

class VenComisionLiquidacionVentas(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        accion = request.POST['accion']
        try:
            if accion == 'consultar_comisiones':
                vendedorid = request.POST.get('vendedorid', '')
                ruc = request.POST.get('vendedor_ruc', '')

                try:
                    if ruc:
                        vendedor = EmpEmpleados.objects.get(cedula=ruc)
                    else:
                        vendedor = EmpEmpleados.objects.get(pk=vendedorid)
                except:
                    vendedor = None

                if vendedor is not None:
                    fecha_corte = self.request.POST.get('fecha_corte', '')
                    fecha_corte = datetime.datetime.strptime(fecha_corte, '%Y-%m-%d').date()

                    hoy = datetime.datetime.now()
                    total_debe = Decimal('0.0')
                    total_haber = Decimal('0.0')
                    total_saldo = Decimal('0.0')
                    total_abonos = 0
                    total_comision_ventas = Decimal('0.0')
                    total_comision = Decimal('0.0')
                    total_pagos_comision = Decimal('0.0')

                    ctotales = 0
                    pendientes = 0
                    parciales = 0
                    supervision = 0

                    listado_deuda_cartillas = []
                    contador = 0
                    ventas_nuevas = 0

                    try:
                        ultimo_pago = VenLiquidacionComision.objects.filter(
                            anulado=False,
                            fecha__date__lte=fecha_corte,
                            vendedor_id=vendedor.id
                        ).order_by('-fecha')[0]

                        if ultimo_pago is not None:
                            ventas_nuevas = VenLiquidacionMovimientos.objects.filter(
                                anulado=False,
                                fecha__date__lte=fecha_corte,
                                fecha__date__gt=ultimo_pago.fecha.date(),
                                vendedor_id=vendedor.id,
                                saldo__gt=0,
                                credito=False
                            ).count()
                    except:
                        pass

                    for m in VenLiquidacionMovimientos.objects.filter(
                        anulado=False,
                        fecha__date__lte=fecha_corte,
                        vendedor_id=vendedor.id,
                        saldo__gt=0,
                        credito=False,
                    ).order_by('fecha', 'cliente__nombre'):

                        diferencia = fecha_corte - m.fecha.date()
                        try:
                            supervisor = EmpEmpleados.objects.get(pk=m.supervisorid).nombre
                        except:
                            supervisor = ''

                        debe = CliClientesDeudas.objects.filter(
                            anulado=False,
                            numcartilla=m.numcartilla,
                            cliente_id=m.cliente_id,
                            credito=False,
                            fecha__date__lte=fecha_corte
                        ).aggregate(debe=Coalesce(Sum('valor'), 0))['debe']

                        debe = round(Decimal(debe), 2)
                        total_debe += debe

                        pagos = CliClientesDeudas.objects.filter(
                            anulado=False,
                            numcartilla=m.numcartilla,
                            cliente_id=m.cliente_id,
                            credito=True,
                            fecha__date__lte=fecha_corte
                        ).aggregate(haber=Coalesce(Sum('valor'), 0), cantidad=Count('valor'))

                        abonos = int(pagos['cantidad'])
                        haber = round(Decimal(pagos['haber']), 2)

                        pagos_comision = VenLiquidacionMovimientos.objects.filter(
                            anulado=False,
                            numcartilla=m.numcartilla,
                            cliente_id=m.cliente_id,
                            credito=True,
                            fecha__date__lte=fecha_corte
                        ).aggregate(comision=Coalesce(Sum('valor'), 0))['comision']

                        pagos_comision = round(Decimal(pagos_comision), 2)
                        total_pagos_comision +=pagos_comision

                        total_abonos += abonos
                        total_haber += haber

                        saldo = round(debe - haber, 2)
                        total_saldo += saldo

                        comision = Decimal('0.00')
                        porcentaje = '0'
                        color = ''

                        if m.numcartilla in lista_cartillas_totales:
                            comision = round(m.valor - pagos_comision, 2)
                            estado = ESTADO_COMISION[0]
                            porcentaje = '100'
                            ctotales += 1
                            color = 'success'
                        elif m.numcartilla in lista_cartillas_parcial:
                            comision = round(m.valor / 2, 2)
                            estado = ESTADO_COMISION[1]
                            porcentaje = '50'
                            color = 'info'
                            parciales += 1
                        else:

                            if saldo <= 0:
                                comision = round(m.valor - pagos_comision, 2)
                                estado = ESTADO_COMISION[0]
                                porcentaje = '100'
                                ctotales += 1
                                color = 'success'
                            elif haber >= round(debe * MINIMO_ABONO, 2) and diferencia.days <= MAXIMO_DIAS_CREDITO and pagos_comision <= 0:
                                comision = round(m.valor / 2, 2)
                                estado = ESTADO_COMISION[1]
                                porcentaje = '50'
                                color = 'info'
                                parciales += 1
                            elif pagos_comision > 0 and diferencia.days <= MAXIMO_DIAS_CREDITO and saldo <= 0:
                                comision = round(m.valor - pagos_comision, 2)
                                estado = ESTADO_COMISION[0]
                                porcentaje = '100'
                                ctotales += 1
                                color = 'success'
                            elif diferencia.days > MAXIMO_DIAS_CREDITO:
                                estado = ESTADO_COMISION[3]
                                supervision += 1
                            else:
                                estado = ESTADO_COMISION[2]
                                pendientes += 1

                        total_comision += comision
                        total_comision_ventas += round(m.valor, 2)

                        item = {
                            'movimientoid': m.id,
                            'fecha': m.fecha.date(),
                            'contado': m.contado,
                            'contado_nombre': 'CONTADO' if m.contado else 'CREDITO',
                            'dias': diferencia.days,
                            'documentoid': m.documentoid,
                            'numcartilla': m.numcartilla,
                            'clienteid': m.cliente_id,
                            'cliente': m.cliente.nombre,
                            'valor_credito': debe,
                            'valor_comision_venta': round(m.valor, 2),
                            'valor_comision': comision,
                            'debe': debe,
                            'haber': haber,
                            'saldo': saldo,
                            'abonos': abonos,
                            'supervisorid': m.supervisorid,
                            'supervisor': supervisor,
                            'estado': estado[0],
                            'estado_nombre': estado[1],
                            'procesar': True if comision > 0 else False,
                            'porcentaje': porcentaje,
                            'porc_color': color,
                            'pagos_comision': pagos_comision
                        }
                        listado_deuda_cartillas.append(item)
                        contador += 1

                    pendientes = (contador - ventas_nuevas)
                    total_ventas = ventas_nuevas + pendientes

                    data['detalle_comisiones'] = listado_deuda_cartillas
                    data['totales'] = {
                        'total_debe': total_debe,
                        'total_haber': total_haber,
                        'total_saldo': total_saldo,
                        'total_abonos': total_abonos,
                        'total_comision_ventas': total_comision_ventas,
                        'total_comision': total_comision,
                        'total_pagos_comision': total_pagos_comision,
                        'items': total_ventas,
                        'ctotales': ctotales,
                        'pendientes': pendientes,
                        'pendientes_nuevas': (total_ventas - parciales - ctotales - supervision),
                        'parciales': parciales,
                        'supervision': supervision,
                        'ventas_nuevas': ventas_nuevas
                    }
                    data['vendedor'] = {
                        'id': vendedor.id,
                        'codigo': vendedor.codigo,
                        'ruc': vendedor.cedula,
                        'nombre': vendedor.nombre
                    }
                    data['resp'] = True
                else:
                    raise Exception('No se encontro datos del vendedor')
                return JsonResponse(data, status=200)

            if accion == 'consultar_comisiones_pendientes':

                pendienteid = request.POST.get('pendienteid')
                try:
                    cpendiente = VenLiquidacionComisionTemporal.objects.get(pk=pendienteid, anulado=False)
                except:
                    raise Exception('No se encontro comisiones pendientes')

                pendiente = {
                    'pendienteid': cpendiente.id,
                    'fecha': cpendiente.fecha.date(),
                    'tipo': cpendiente.tipo,
                    'vendedor': {
                        'id': cpendiente.vendedor.id,
                        'codigo': cpendiente.vendedor.codigo,
                        'ruc': cpendiente.vendedor.cedula,
                        'nombre': cpendiente.vendedor.nombre
                    },
                    'vendedorid': cpendiente.vendedor.id,
                    'subtotal': cpendiente.subtotal,
                    'descuento': cpendiente.descuento,
                    'impuesto': cpendiente.impuesto,
                    'total': cpendiente.total,
                    'items': []
                }

                total_debe = Decimal('0.0')
                total_haber = Decimal('0.0')
                total_saldo = Decimal('0.0')
                total_abonos = 0
                total_comision_ventas = Decimal('0.0')
                total_comision = Decimal('0.0')

                ctotales = 0
                pendientes = 0
                parciales = 0
                supervision = 0
                contador = 0

                for d in cpendiente.venliquidacioncomisiondetalletemporal_set.filter(anulado=False):
                    color = ''
                    if d.estado == '2':
                        color = 'info'
                    elif d.estado == '1':
                        color = 'success'

                    pendiente['items'].append(
                        {
                            'pdetalleid': d.id,
                            'movimientoid': d.movimientoid,
                            'fecha': d.fecha.date(),
                            'contado': d.contado,
                            'contado_nombre': 'CONTADO' if d.contado else 'CREDITO',
                            'dias': d.dias,
                            'documentoid': d.factura_id,
                            'numcartilla': d.numcartilla,
                            'clienteid': d.cliente_id,
                            'cliente': d.cliente.nombre,
                            'valor_credito': round(d.valor_credito, 2),
                            'valor_comision_venta': round(d.valor_comision, 2),
                            'valor_comision': round(d.valor_pago, 2),
                            'debe': round(d.valor_credito, 2),
                            'haber': round(d.valor_abono, 2),
                            'saldo': round(d.saldo, 2),
                            'abonos': d.abonos,
                            'supervisorid': d.supervisor_id,
                            'supervisor': d.supervisor.nombre,
                            'estado': d.estado,
                            'estado_nombre': d.get_estado_display(),
                            'procesar': d.procesar,
                            'porcentaje': round(d.porcentaje, 2),
                            'porc_color': color,
                            'pagos_comision': round(d.valor_pagado, 2)
                        }
                    )
                    total_debe += round(d.valor_credito, 2)
                    total_haber += round(d.valor_abono, 2)
                    total_saldo += round(d.saldo, 2)
                    total_abonos += d.abonos
                    total_comision_ventas += round(d.valor_comision, 2)

                    if d.procesar:
                        total_comision += round(d.valor_pago, 2)
                        contador += 1

                    if d.estado == '1':
                        ctotales += 1
                    elif d.estado == '2':
                        parciales += 1
                    elif d.estado == '3':
                        pendientes += 1
                    elif d.estado == '4':
                        supervision += 1

                data['totales'] = {
                    'total_debe': total_debe,
                    'total_haber': total_haber,
                    'total_saldo': total_saldo,
                    'total_abonos': total_abonos,
                    'total_comision_ventas': total_comision_ventas,
                    'total_comision': total_comision,
                    'items': contador,
                    'ctotales': ctotales,
                    'pendientes': pendientes,
                    'parciales': parciales,
                    'supervision': supervision
                }
                data['pendiente'] = pendiente
                data['resp'] = True

                return JsonResponse(data, status=200)

            if accion == 'guardar_comisiones_temporal':

                with transaction.atomic():
                    json_data = json.loads(request.POST['comision'])
                    json_resumen = json.loads(request.POST['totales'])

                    fecha = datetime.datetime.strptime(json_data['fecha'], '%Y-%m-%d')
                    vendedor = json_data['vendedor']

                    if VenLiquidacionComisionTemporal.objects.filter(anulado=False,pk=json_data['pendienteid']).exists():

                        comision = VenLiquidacionComisionTemporal.objects.get(pk=json_data['pendienteid'])
                        comision.subtotal = Decimal(json_data['subtotal'])
                        comision.impuesto = Decimal(json_data['impuesto'])
                        comision.total = Decimal(json_data['total'])
                        comision.detalle = vendedor['nombre']
                        comision.comision_pendiente = json_resumen['pendientes']
                        comision.ventas_nuevas = json_resumen['ventas_nuevas']
                        comision.comision_totales = json_resumen['items']
                        comision.liquidacion_parcial = json_resumen['parciales']
                        comision.liquidacion_total = json_resumen['ctotales']
                        comision.liquidacion_pendiente = json_resumen['pendientes_nuevas']
                        comision.liquidacion_supervicion = json_resumen['supervision']

                        comision.save()
                        for item in json_data['items']:
                            detalle = '{}: comision ${}'.format(vendedor['nombre'], item['valor_comision'])
                            try:
                                dt = VenLiquidacionComisionDetalleTemporal.objects.get(pk=item['pdetalleid'])
                                dt.contado = item['contado']
                                dt.valor_credito = item['valor_credito']
                                dt.valor_comision = item['valor_comision_venta']
                                dt.valor_pago = item['valor_comision']
                                dt.valor_abono = item['haber']
                                dt.saldo = item['saldo']
                                dt.abonos = item['abonos']
                                dt.dias = item['dias']
                                dt.porcentaje = item['porcentaje']
                                dt.supervisor_id = item['supervisorid']
                                dt.detalle = detalle
                                dt.estado = item['estado']
                                dt.procesar = item['procesar']
                                dt.valor_pagado = item['pagos_comision']
                                dt.save()
                            except:
                                continue
                        data['resp'] = True

                    else:
                        comision = VenLiquidacionComisionTemporal(
                            fecha=fecha,
                            tipo=json_data['tipo'],
                            ruc=vendedor['ruc'],
                            vendedor_id=json_data['vendedorid'],
                            subtotal=json_data['subtotal'],
                            total=json_data['total'],
                            detalle=vendedor['nombre'],
                            comision_pendiente=json_resumen['pendientes'],
                            ventas_nuevas=json_resumen['ventas_nuevas'],
                            comision_totales=json_resumen['items'],
                            liquidacion_parcial=json_resumen['parciales'],
                            liquidacion_total=json_resumen['ctotales'],
                            liquidacion_pendiente=json_resumen['pendientes_nuevas'],
                            liquidacion_supervicion=json_resumen['supervision']
                        )
                        comision.save()
                        for item in json_data['items']:
                            detalle = '{}: comision ${}'.format(vendedor['nombre'], item['valor_comision'])

                            comisionDt = VenLiquidacionComisionDetalleTemporal(
                                comision_id=comision.id,
                                movimientoid=item['movimientoid'],
                                numcartilla=item['numcartilla'],
                                cliente_id=item['clienteid'],
                                factura_id=item['documentoid'],
                                contado=item['contado'],
                                fecha=datetime.datetime.strptime(item['fecha'], '%Y-%m-%d'),
                                valor_credito=item['valor_credito'],
                                valor_comision=item['valor_comision_venta'],
                                valor_pago=item['valor_comision'],
                                valor_abono=item['haber'],
                                saldo=item['saldo'],
                                abonos=item['abonos'],
                                dias=item['dias'],
                                porcentaje=item['porcentaje'],
                                supervisor_id=item['supervisorid'],
                                detalle=detalle,
                                estado=item['estado'],
                                divisionid=comision.divisionid,
                                procesar=item['procesar'],
                                valor_pagado=item['pagos_comision']
                            )
                            comisionDt.save()
                        data['resp'] = True

            if accion == 'guardar_comisiones':

                with transaction.atomic():

                    json_data = json.loads(request.POST['comision'])
                    json_resumen = json.loads(request.POST['totales'])

                    fecha = datetime.datetime.strptime(json_data['fecha'], '%Y-%m-%d')
                    vendedor = json_data['vendedor']

                    comision = VenLiquidacionComision(
                        fecha=fecha,
                        tipo=json_data['tipo'],
                        ruc=vendedor['ruc'],
                        vendedor_id=json_data['vendedorid'],
                        subtotal=json_data['subtotal'],
                        total=json_data['total'],
                        detalle=vendedor['nombre'],
                        comision_pendiente=json_resumen['pendientes'],
                        ventas_nuevas=json_resumen['ventas_nuevas'],
                        comision_totales=json_resumen['items'],
                        liquidacion_parcial=json_resumen['parciales'],
                        liquidacion_total=json_resumen['ctotales'],
                        liquidacion_pendiente=json_resumen['pendientes_nuevas'],
                        liquidacion_supervicion=json_resumen['supervision']
                    )
                    comision.save()

                    for item in json_data['items']:
                        if item['procesar']:
                            detalle = '{}: comision ${}'.format(vendedor['nombre'], item['valor_comision'])
                            comisionDt = VenLiquidacionComisionDetalle(
                                comision_id=comision.id,
                                numcartilla=item['numcartilla'],
                                cliente_id=item['clienteid'],
                                factura_id=item['documentoid'],
                                contado=item['contado'],
                                fecha=datetime.datetime.strptime(item['fecha'], '%Y-%m-%d'),
                                valor_credito=item['valor_credito'],
                                valor_comision=item['valor_comision_venta'],
                                valor_pago=item['valor_comision'],
                                supervisor_id=item['supervisorid'],
                                detalle=detalle,
                                estado=item['estado'],
                                divisionid=comision.divisionid,
                                valor_abono=item['haber'],
                                saldo =item['saldo'],
                                abonos =item['abonos'],
                                dias =item['dias'],
                                porcentaje =item['porcentaje']
                            )
                            comisionDt.save()
                            movimiento = VenLiquidacionMovimientos(
                                fecha=fecha,
                                vendedor_id=comision.vendedor_id,
                                supervisorid=item['supervisorid'],
                                numcartilla=item['numcartilla'],
                                cliente_id=item['clienteid'],
                                documentoid=comision.id,
                                numero=comision.numero,
                                detalle=detalle,
                                valor=item['valor_comision'],
                                valor_base=item['valor_comision'],
                                movimiento_id=item['movimientoid'],
                                tipo=comision.tipo,
                                credito=True,
                                estado=item['estado'],
                                divisionid=comision.divisionid
                            )
                            movimiento.save()
                            m = VenLiquidacionMovimientos.objects.get(pk=item['movimientoid'])
                            if (Decimal(m.saldo) - Decimal(movimiento.valor)) > 0:
                                m.saldo = round(Decimal(m.saldo) - Decimal(movimiento.valor), 2)
                            else:
                                m.saldo = 0
                            m.estado = movimiento.estado
                            m.save()

                    data['documentoid'] = comision.id
                    data['resp'] = True
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, status=200)

    def get(self, request, *args, **kwargs):
        data = {}
        addUserData(request, data)
        try:
            return render(request, 'venta/ven_liquidacion_comision_ventas.html', data)
        except Exception as e:
            return redirect('/')

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def get_consulta_pendientes(request):
    data = {'resp': False, 'error': ''}
    if request.method == 'GET':
        try:
            accion = request.GET.get('accion')
            if accion == 'buscar_pendientes':
                criterio = request.GET.get('criterio', '')
                pendientes = VenLiquidacionComisionTemporal.objects.filter(
                    Q(anulado=False),
                    Q(pagada=False),
                    Q(vendedor__nombre__icontains=criterio),
                ).order_by('vendedor__nombre')[:20]

                lista_pendientes = []
                for p in pendientes:
                    lista_pendientes.append({
                        "id": p.id,
                        "fecha": p.fecha.date().today(),
                        "vendedorid": p.vendedor.id,
                        "nombre": p.vendedor.nombre,
                        "total": p.total
                    })
                return JsonResponse({"pendientes": lista_pendientes, "resp": True}, status=200)

        except Exception as e:
            data['error'] = 'error: ' + str(e)
    return JsonResponse(data, status=200)

def get_procesar_facturas(request):
    if request.method == 'GET':
        mensaje = ''
        try:
            for f in VenFacturas.objects.filter(anulado=False, tipo='VEN-FA', creadopor__in=(
                    'REC-COB-01', 'REC-COB-02', 'SVC-01', 'SVC-02', 'CYANQUIG', 'XYZ'), caja__cobertura=True):

                liqmovimientos = VenLiquidacionMovimientos.objects.filter(
                    anulado=False, numcartilla=f.numcartilla,
                    cliente_id=f.cliente_id,
                    documentoid=f.id
                )

                if not liqmovimientos.exists():

                    total_comision = Decimal('0.0')
                    for d in f.venfacturasdetalle_set.all():
                        grupo = d.producto.grupo
                        # rentabilidad_costo = Decimal('0.0')

                        if f.contado:
                            # rentabilidad_costo = grupo.rentabilidad_costo_contado
                            comision_pvp = grupo.comision_pvp_contado
                        else:
                            # rentabilidad_costo = grupo.rentabilidad_costo_credito
                            comision_pvp = grupo.comision_pvp_credito

                        # d.valor_rentabilidad = d.costo * (rentabilidad_costo/100)
                        d.valor_comision = round(d.total * (comision_pvp / 100), 2)
                        d.save()
                        total_comision += d.valor_comision

                    f.total_comision = total_comision
                    f.save()

                    movimiento = VenLiquidacionMovimientos(
                        fecha=f.fecha,
                        vendedor_id=f.vendedorid,
                        supervisorid=f.entregadorid,
                        numcartilla=f.numcartilla,
                        cliente_id=f.cliente_id,
                        documentoid=f.id,
                        contado=f.contado,
                        numero=f.numero,
                        detalle=f.detalle,
                        valor_credito=f.total,
                        valor=f.total_comision,
                        valor_base=round(f.total_comision * f.cambio, 2),
                        divisaid=f.divisaid,
                        cambio=f.cambio,
                        saldo=f.total_comision,
                        tipo=f.tipo.strip(),
                        credito=False,
                        estado='3',
                        sucursalid=f.sucursalid,
                        divisionid=f.division_id,
                        creadopor=f.creadopor,
                        creadodate=f.creadodate
                    )
                    movimiento.save()
            mensaje = 'procesado'
        except Exception as e:
            mensaje = str(e)
        messages.add_message(request, 40, mensaje)
        return redirect('/')

class CliCotizacionesPersonalizada(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        accion = request.POST['accion']

    def get(self, request, *args, **kwargs):
        data = {}
        addUserData(request, data)
        try:
            caja = request.user.segusuarioparametro.caja
            if caja is None:
                raise Exception('No se encontro caja asociado al usuario..')

            data['caja_id'] = caja.id
            data['sucursal'] = SisSucursales.objects.get(codigo=caja.sucursal)
            data['bodegas'] = InvBodegas.objects.filter(anulado=False, sucursal=caja.sucursal)
            #data['tipo_modelo'] = TIP_MODELO

            if caja.bodega is not None:
                data['bodega_id'] = caja.bodega.id

            if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                data['disabled'] = True
            return render(request, 'venta/cli_cotizacion_personalizada.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')

