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
from banco.models import BanBancos
from cliente.models import CliClientes,CliRubros
from contabilidad.models import AccAsientos
from contadores.fn_contador import get_contador_sucdiv, get_contador_sucuencia_preimpresa
from empleado.models import EmpEmpleados, EmpRubros
from pedido.models import VenOrdenPedidos
from sistema.constantes import USER_ALL_PERMISOS, PEDIDOS_CONTROLA_STOCK
from sistema.funciones import addUserData
from sistema.models import SisSucursales, SisParametros, SisDivisiones
from venta.models import VenFacturas, VenFacturasDetalle

class PosPuntoVentaMayoristaFactura(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        try:
            accion = request.POST.get('accion')
            if accion == 'pedido_procesar_factura':

                with transaction.atomic():
                    try:
                        cliente = CliClientes.objects.get(pk=request.POST.get('cliente_id'))
                    except:
                        raise Exception('No se encontro cliente seleccionado..')

                    try:
                        caja = BanBancos.objects.get(pk=request.POST.get('caja_id'))
                    except:
                        raise Exception('No se encontro caja banco..')

                    termino = request.POST.get('termino')
                    factura_total = Decimal(request.POST.get('factura_total',0))
                    empleado = None
                    forma_pago = request.POST.get('forma_pago')
                    termino_dias = 8

                    if forma_pago != 'EFE':
                        try:
                            if cliente.empleadoid is not None and cliente.empleadoid.strip() != '':
                                empleado = EmpEmpleados.objects.get(pk=cliente.empleadoid)
                                if (cliente.cupo - (cliente.get_saldo_total() + empleado.get_saldo_total_empleado())) < factura_total:
                                    raise Exception('La orden excede el cupo disponible del Cliente.')
                            else:
                                if (cliente.cupo - cliente.get_saldo_total()) < factura_total:
                                    raise Exception('La orden excede el cupo disponible del Cliente.')
                        except:
                            raise Exception('No se pudo determinar el cupo disponible del Cliente')

                        try:
                            termino_dias = int(SisParametros.objects.get(pk=cliente.termino).valor)
                        except:
                            termino_dias = 8

                    controla_items = False
                    try:
                        if SisParametros.objects.get(codigo='POS-CONTROLAR-MAXIMO-LINEAS').valor.upper() == 'SI':
                            controla_items = True
                    except:
                        pass

                    if controla_items:
                        try:
                            items_maximo = int(SisParametros.objects.get(codigo='POS-MAX-ITEMS').valor)
                        except:
                            raise Exception('No de encontro parametro maximo items..')
                    else:
                        items_maximo = 100

                    contado = bool(int(request.POST.get('contado')))
                    tipo_factura = request.POST.get('tipo_factura')
                    tipo = ''

                    efectivo = Decimal('0.00')
                    credito = Decimal('0.00')
                    cheque = Decimal('0.00')
                    tarjeta = Decimal('0.00')

                    if contado and forma_pago == 'EFE':
                        if tipo_factura == 'FA':
                            tipo = 'POS-FA'
                        else:
                            tipo = 'POS-NV'

                    elif forma_pago == 'CHE':
                        tipo = 'VEN-CHE'
                        cheque = factura_total
                    elif forma_pago == 'CRE':
                        if cliente.empleadoid is not None and empleado is not None:
                            if tipo_factura == 'FA':
                                tipo = 'EMP-FA'
                            else:
                                tipo = 'EMP-NV'
                        else:
                            if tipo_factura == 'FA':
                                tipo = 'VEN-FA'
                            else:
                                tipo = 'VEN-NV'
                        credito = factura_total
                    elif forma_pago == 'TAR':
                        tipo='VEN-TA'
                        tarjeta = factura_total

                    json_data = json.loads(request.POST.get('factura'))
                    cotizacionid = json_data['cotizacion_id']
                    sucursalid = json_data['sucursalid']
                    divisionid = json_data['divisionid']

                    if tipo_factura == 'NV':
                        try:
                            divisionid = SisDivisiones.objects.get(informal=True).id
                        except:
                            raise Exception('No se encontro division informal ID.')

                    divisaid = json_data['divisaid']
                    controla_stock = bool(int(json_data['controla_stock'],0))
                    fecha = datetime.datetime.strptime(json_data['fecha'], '%d/%m/%Y')

                    paginas = int((len(json_data['items']) - 1)/items_maximo) + 1
                    lista_facturas = []

                    for i in range(paginas):

                        if contado and forma_pago == 'EFE':
                            facturaid = get_contador_sucdiv('VEN_FACTURAS-ID-', '{}{}'.format(sucursalid, divisionid[-1]))
                            if tipo_factura == 'FA':
                                try:
                                    fact_preimpresa = get_contador_sucuencia_preimpresa('POS-SECUENCIA-FA-{}'.format(caja.serie),caja.serie)
                                    detalle = '{} FAC:{}'.format(cliente.nombre, fact_preimpresa)
                                except:
                                    raise Exception('No se puede generar la secuencia Factura Pre-impresa..')
                            else:
                                fact_preimpresa = ''
                                detalle = '{} FAC: {}'.format(cliente.nombre, facturaid)

                            factura = VenFacturas(
                                id=facturaid,
                                ordenid=cotizacionid,
                                numero=facturaid,
                                secuencia=facturaid,
                                cliente_id=cliente.id,
                                detalle=cliente.nombre,
                                ruc=cliente.ruc,
                                vendedorid=cliente.vendedor_id if cliente.vendedor_id is not None else '',
                                empleadoid=cliente.empleadoid if cliente.empleadoid is not None else '',
                                caja_id=caja.id,
                                terminoid=cliente.termino,
                                division_id=divisionid,
                                bodega_id=json_data['bodegaid'],
                                contado=contado,
                                fecha=fecha,
                                entregado=fecha,
                                tipo=tipo,
                                divisaid=divisaid,
                                fecha_cheque=fecha,
                                vence=fecha,
                                fecha_oc=datetime.datetime.strptime('01/01/1900', '%d/%m/%Y'),
                                forma_pago=forma_pago,
                                nocontrola_stock=True,
                                nota=json_data['nota'],
                                sucursalid=sucursalid,
                                ptg_iva=Decimal(json_data['ptg_iva']),
                                archivo_sri=True if tipo_factura =='FA' else False,
                                fact_preimpresa=fact_preimpresa,
                                efectivo=Decimal(json_data['efectivo']),
                                vuelto_cliente=Decimal(json_data['vuelto_cliente']),
                                zona_id=cliente.zona_id if cliente.zona_id is not None else '',
                                reimpreso=True,
                                tipo_modelo='3',
                                nota2=json_data['observacion']
                            )
                            factura.save()

                            for i in range(items_maximo):
                                try:
                                    item = json_data['items'].pop(0)
                                except:
                                    break

                                if item['cantidad'] > 0:

                                    detalleid = get_contador_sucdiv('VEN_FACTURAS_DT-ID-','{}{}'.format(sucursalid, divisionid[-1]))
                                    cantidad = round(Decimal(item['cantidad']) * Decimal(item['factor']), 2)

                                    factura_detalle = VenFacturasDetalle(
                                        id=detalleid,
                                        factura_id=factura.id,
                                        producto_id=item['productoid'],
                                        bodega_id=factura.bodega_id,
                                        cantidad=cantidad,
                                        precio=item['precio'],
                                        costo=item['costo_compra'],
                                        subtotal=item['subtotal'],
                                        tasa_descuento=item['tasa_descuento'],
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
                                        cursor.execute("{CALL INV_ProductosCardex_Insert_Pos_Mayorista(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                            factura_detalle.producto_id,
                                            factura_detalle.bodega_id,
                                            '',
                                            factura.id,
                                            factura.id,
                                            fecha,
                                            tipo,
                                            detalle,
                                            True,
                                            cantidad,
                                            factura_detalle.costo,
                                            divisaid,
                                            1,
                                            divisionid,
                                            request.user.username,
                                            sucursalid,
                                            ''
                                        ))

                            totales = factura.venfacturasdetalle_set.aggregate(
                                tsubtotal=Coalesce(Sum('subtotal'),0),
                                tdescuento=Coalesce(Sum('descuento'),0),
                                timpuesto=Coalesce(Sum('impuesto'),0),
                                ttotal=Coalesce(Sum('total'),0),
                                tcomision=Coalesce(Sum('valor_comision'),0)
                            )

                            factura.subtotal = totales['tsubtotal']
                            factura.descuento = totales['tdescuento']
                            factura.impuesto = totales['timpuesto']
                            factura.total = totales['ttotal']
                            factura.total_comision = totales['tcomision']

                            base_iva = factura.venfacturasdetalle_set.filter(impuesto__gt=0).aggregate(
                                tsubtotal_iva=Coalesce(Sum('subtotal'),0),
                                tdescuento_iva=Coalesce(Sum('descuento'),0)
                            )

                            base_cero = factura.venfacturasdetalle_set.filter(impuesto__lte=0).aggregate(
                                tsubtotal_cero=Coalesce(Sum('subtotal'),0),
                                tdescuento_cero=Coalesce(Sum('descuento'), 0)
                            )

                            factura.subtotal_iva = base_iva['tsubtotal_iva']
                            #factura.descuento_iva =base_iva['tdescuento_iva']
                            factura.descuento_iva = base_cero['tdescuento_cero']

                            factura.subtotal_cero = base_cero['tsubtotal_cero']
                            #factura.descuento_cero = base_cero['tdescuento_cero']
                            factura.descuento_cero = base_iva['tdescuento_iva']
                            factura.save()

                        elif forma_pago == 'CRE':

                            asientoid = get_contador_sucdiv('ACC_ASIENTOS-ID-','{}{}'.format(sucursalid, divisionid[-1]))
                            asiento_numero = get_contador_sucdiv('ACC_ASIENTOS-NUMBER-','{}{}'.format(sucursalid, divisionid[-1]))
                            facturaid = get_contador_sucdiv('VEN_FACTURAS-ID-','{}{}'.format(sucursalid, divisionid[-1]))

                            if tipo_factura == 'FA':
                                try:
                                    fact_preimpresa = get_contador_sucuencia_preimpresa('POS-SECUENCIA-FA-{}'.format(caja.serie), caja.serie)
                                    detalle = '{} FAC:{}-{}'.format(cliente.nombre,facturaid, fecha)
                                except:
                                    raise Exception('No se puede generar la secuencia Factura Pre-impresa..')
                            else:
                                fact_preimpresa = ''
                                detalle = '{} FAC:{}-'.format(cliente.nombre,facturaid, fecha)

                            try:
                                fecha_vence = fecha + datetime.timedelta(days=termino_dias)
                            except:
                                fecha_vence = datetime.datetime.now() + datetime.timedelta(days=termino_dias)

                            factura = VenFacturas(
                                id=facturaid,
                                ordenid=cotizacionid,
                                numero=facturaid,
                                secuencia=facturaid,
                                cliente_id=cliente.id,
                                detalle=cliente.nombre,
                                ruc=cliente.ruc,
                                asientoid=asientoid,
                                vendedorid=cliente.vendedor_id if cliente.vendedor_id is not None else '',
                                empleadoid=cliente.empleadoid if cliente.empleadoid is not None else '',
                                caja_id=caja.id,
                                terminoid=cliente.termino,
                                division_id=divisionid,
                                bodega_id=json_data['bodegaid'],
                                contado=contado,
                                fecha=fecha,
                                entregado=fecha,
                                tipo=tipo,
                                divisaid=divisaid,
                                fecha_cheque=fecha,
                                vence= fecha_vence,
                                fecha_oc=datetime.datetime.strptime('01/01/1900', '%d/%m/%Y'),
                                forma_pago=forma_pago,
                                nocontrola_stock=False,
                                nota=json_data['nota'],
                                sucursalid=sucursalid,
                                ptg_iva=Decimal(json_data['ptg_iva']),
                                archivo_sri=True if tipo_factura == 'FA' else False,
                                fact_preimpresa=fact_preimpresa,
                                zona_id=cliente.zona_id if cliente.zona_id is not None else '',
                                credito=credito,
                                dias_credito=termino_dias if termino_dias > 0 else 8,
                                reimpreso=True,
                                tipo_modelo='3',
                                nota2=json_data['observacion']
                            )
                            factura.save()

                            for i in range(items_maximo):
                                try:
                                    item = json_data['items'].pop(0)
                                except:
                                    break

                                if item['cantidad'] > 0:

                                    detalleid = get_contador_sucdiv('VEN_FACTURAS_DT-ID-','{}{}'.format(sucursalid, divisionid[-1]))
                                    cantidad = round(Decimal(item['cantidad']) * Decimal(item['factor']), 2)

                                    factura_detalle = VenFacturasDetalle(
                                        id=detalleid,
                                        factura_id=factura.id,
                                        producto_id=item['productoid'],
                                        bodega_id=factura.bodega_id,
                                        cantidad=cantidad,
                                        precio=item['precio'],
                                        costo=item['costo_compra'],
                                        subtotal=item['subtotal'],
                                        tasa_descuento=item['tasa_descuento'],
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
                                        cursor.execute("{CALL INV_ProductosCardex_Insert_Pos_Mayorista(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                            factura_detalle.producto_id,
                                            factura_detalle.bodega_id,
                                            asientoid,
                                            factura.id,
                                            factura.id,
                                            fecha,
                                            tipo,
                                            detalle,
                                            True,
                                            cantidad,
                                            factura_detalle.costo,
                                            divisaid,
                                            1,
                                            divisionid,
                                            request.user.username,
                                            sucursalid,
                                            ''
                                        ))

                            totales = factura.venfacturasdetalle_set.aggregate(
                                tsubtotal=Coalesce(Sum('subtotal'), 0),
                                tdescuento=Coalesce(Sum('descuento'), 0),
                                timpuesto=Coalesce(Sum('impuesto'), 0),
                                ttotal=Coalesce(Sum('total'), 0),
                                tcomision=Coalesce(Sum('valor_comision'), 0)
                            )

                            factura.subtotal = totales['tsubtotal']
                            factura.descuento = totales['tdescuento']
                            factura.impuesto = totales['timpuesto']
                            factura.total = totales['ttotal']
                            factura.total_comision = totales['tcomision']

                            base_iva = factura.venfacturasdetalle_set.filter(impuesto__gt=0).aggregate(
                                tsubtotal_iva=Coalesce(Sum('subtotal'), 0),
                                tdescuento_iva=Coalesce(Sum('descuento'), 0)
                            )

                            base_cero = factura.venfacturasdetalle_set.filter(impuesto__lte=0).aggregate(
                                tsubtotal_cero=Coalesce(Sum('subtotal'), 0),
                                tdescuento_cero=Coalesce(Sum('descuento'), 0)
                            )


                            factura.subtotal_iva = base_iva['tsubtotal_iva']
                            # factura.descuento_iva =base_iva['tdescuento_iva']
                            factura.descuento_iva = base_cero['tdescuento_cero']

                            factura.subtotal_cero = base_cero['tsubtotal_cero']
                            # factura.descuento_cero = base_cero['tdescuento_cero']
                            factura.descuento_cero = base_iva['tdescuento_iva']
                            factura.save()

                            total_debe = Decimal(0.00)
                            total_haber = Decimal(0.00)

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

                            if cliente.empleadoid is not None and empleado is not None:
                                codigo_rubro = 'EMP-RUBRO-FACTURA-ID'
                                parametro = SisParametros.objects.get(codigo=codigo_rubro)
                                rubro = EmpRubros.objects.get(id=parametro.valor.strip())
                            else:
                                codigo_rubro = 'CLI-RUBRO-FACTURA-ID'
                                parametro = SisParametros.objects.get(codigo=codigo_rubro)
                                rubro = CliRubros.objects.get(id=parametro.valor.strip())

                            # Asiento contable DEBE
                            valor_base = round(Decimal(factura.total) * Decimal(1.00), 4)
                            with connection.cursor() as cursor:
                                cursor.execute("{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
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
                                raise Exception('Asiento desbalanceado. TOTAL DEBE:{}  TOTAL HABER:{}'.format(total_debe,total_haber))

                            if cliente.empleadoid is not None and empleado is not None:
                                emleado_deudaid = get_contador_sucdiv('EMP_EMPLEADOS_DEUDAS-ID-','{}{}'.format(sucursalid, divisionid[-1]))

                                with connection.cursor() as cursor:

                                    valor_base = round(factura.total * Decimal(1.00), 2)
                                    cursor.execute(
                                        "{CALL EMP_EmpleadosDeudas_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                        (
                                            emleado_deudaid,
                                            empleado.id,
                                            factura.id,
                                            asiento.id,
                                            factura.id,
                                            detalle,
                                            round(factura.total, 2),
                                            valor_base,
                                            fecha,
                                            fecha,
                                            rubro.id,
                                            rubro.ctadebe_id,
                                            divisaid,
                                            Decimal(1.00),
                                            round(factura.total, 2),
                                            tipo,
                                            False,
                                            '',
                                            divisionid,
                                            request.user.username,
                                            sucursalid,
                                            ''
                                        ))
                            else:

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

                        lista_facturas.append({
                            'factura_id': factura.id,
                            'cliente_id': cliente.id,
                            'cliente': cliente.nombre,
                            'detalle': detalle,
                            'tipo':tipo_factura,
                            'cotizacion': cotizacionid
                        })

                    try:
                        if cotizacionid:
                            VenOrdenPedidos.objects.filter(numero=cotizacionid,anulado=False).update(estado='5',procesado=True)
                    except:
                        pass

                    data['resp'] = True
                    data['tipo'] = tipo_factura
                    data['documentos'] = lista_facturas
                    return JsonResponse(data, status=200)

        except Exception as e:
            data['error'] = 'error: ' + str(e)
        return JsonResponse(data, status=200)

    def get(self, request, *args, **kwargs):
        data = {"procesar": False}
        addUserData(request, data)
        try:
            pedido_id = kwargs.get("pk", None)

            if pedido_id is not None:
                try:
                    pedido = VenOrdenPedidos.objects.get(pk=pedido_id, anulado=False)
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

                    if pedido.forma_pago == 'CRE':
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
                data['cupo'] = round(cliente.cupo, 2)
                data['saldo_total'] = round(saldo_total, 2)
                data['disponible'] = round(disponible, 2)
                data['procesar'] = True

                return render(request, 'pos/pos_facturar_pedido.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/pos/factura/pedidos/')
