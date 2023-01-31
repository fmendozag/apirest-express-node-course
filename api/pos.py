import datetime
import math
from decimal import Decimal
from django.db import transaction, connection
from django.db.models import Sum, Max, F
from django.db.models.functions import Coalesce
from rest_framework.response import Response
from rest_framework.views import APIView
from cliente.models import CliClientes, CliRubros, CliCotizaciones, CliCotizacionesDetalle
from contabilidad.models import AccAsientos
from contadores.fn_contador import get_contador_sucdiv, get_contador_sucuencia_preimpresa, get_contador
from empleado.models import EmpEmpleados, EmpRubros
from inventario.models import InvProductos
from pos.models import PosAperturaCaja
from sistema.models import SisParametros, SisDivisiones, SisSucursales
from venta.models import VenFacturas, VenFacturasDetalle

class PosSincronizarFacturas(APIView):
    def post(self, request,accion, *args, **kwargs):
        data = {'resp': False}
        try:
            if accion == 'sincronizar':
                with transaction.atomic():

                    dataFactura = self.request.data
                    procesada = bool(int(dataFactura.get('procesada', 0)))
                    anulado = bool(int(dataFactura.get('anulada', 0)))

                    try:
                        cliente_id = dataFactura.get('clienteId',None)
                        if cliente_id is not None:
                            cliente = CliClientes.objects.get(pk=cliente_id)
                        else:
                            cliente = CliClientes.objects.get(pk='0000000001')
                        parametro = SisParametros.objects.get(pk=cliente.termino)
                    except:
                        raise Exception('No se encontro cliente seleccionado..')

                    try:
                        user = self.request.user
                        usuario_parametro= user.segusuarioparametro
                        caja = usuario_parametro.caja
                        sucursalid = SisSucursales.objects.get(codigo=caja.sucursal).codigo
                        divisionid = caja.division.id
                        divisaid = caja.divisa
                    except:
                        raise Exception('No se encontro caja banco..')

                    fecha = datetime.datetime.strptime(dataFactura.get('fecha'), '%d-%m-%Y %H:%M:%S').date()
                    contado = bool(int(dataFactura.get('contado', 1)))

                    try:
                        cotizacion_id = get_contador('CLI_COTIZACIONES-ID', user)
                        cotizacion_numero = get_contador('CLI_COTIZACIONES-NUMBER', user)
                        cotizacion = CliCotizaciones(
                            id=cotizacion_id,
                            numero=cotizacion_numero,
                            tipo='COT-FA',
                            fecha=fecha,
                            cliente_id=cliente.id,
                            nombre=cliente.nombre,
                            vendedor_id=cliente.vendedor_id,
                            divisaid=divisaid,
                            cambio=Decimal('1.00'),
                            atentamente=user.username,
                            validez='15 DIAS',
                            terminoid=cliente.termino,
                            detalle='Pendiente Doc: {}'.format(cliente.nombre),
                            division=divisionid,
                            sucursalid=sucursalid,
                            caja_id=caja.id,
                            caja_code=caja.codigo,
                            contado=contado,
                            empleadoid=cliente.empleadoid.strip(),
                            bodega_id=caja.bodega.id,
                            entregado=fecha,
                            procesado=procesada,
                            pcid='COT-MOVIL',
                            anulado=anulado
                        )
                        cotizacion.save()

                        for item in dataFactura.get('itemsOrdenes'):
                            if item['cantidad'] > 0:
                                try:
                                    producto = InvProductos.objects.get(pk=item['productoId'])
                                except:
                                    continue
                                cotizacion_dt_id = get_contador('CLI_COTIZACIONES_DT-ID', user)
                                cotizacion_detalle = CliCotizacionesDetalle(
                                    id=cotizacion_dt_id,
                                    cotizacion_id=cotizacion.id,
                                    producto_id=producto.id,
                                    nombre=producto.nombre,
                                    bodegaid=cotizacion.bodega_id,
                                    codigo=producto.codigo,
                                    cantidad=item['cantidad'],
                                    precio=item['precio'],
                                    precio_display=item['precioDisplay'],
                                    precio_factor=item['precioFactor'],
                                    precio_final=item['precioFactor'],
                                    costo=item['costo'],
                                    subtotal=item['subtotal'],
                                    tasa_descuento=item['tasaDescuento'],
                                    descuento=item['descuento'],
                                    impuestoid=producto.impuestoid.strip(),
                                    tasa_impuesto=item['tasaImpuesto'],
                                    impuesto=item['impuesto'],
                                    total=item['total'],
                                    empaque=item['empaque'],
                                    factor=item['factor'],
                                    sucursalid=sucursalid,
                                    clase='01',
                                    coniva=True if producto.impuestoid.strip() else False
                                )
                                cotizacion_detalle.save()

                        totales = cotizacion.clicotizacionesdetalle_set.aggregate(
                            tsubtotal=Coalesce(Sum('subtotal'), 0),
                            tdescuento=Coalesce(Sum('descuento'), 0),
                            timpuesto=Coalesce(Sum('impuesto'), 0),
                            ttotal=Coalesce(Sum('total'), 0),
                        )

                        cotizacion.subtotal = totales['tsubtotal']
                        cotizacion.descuento = totales['tdescuento']
                        cotizacion.impuesto = totales['timpuesto']
                        cotizacion.total = totales['ttotal']

                        base_iva = cotizacion.clicotizacionesdetalle_set.filter(impuesto__gt=0).aggregate(
                            tsubtotal_iva=Coalesce(Sum('subtotal'), 0),
                            tdescuento_iva=Coalesce(Sum('descuento'), 0)
                        )

                        base_cero = cotizacion.clicotizacionesdetalle_set.filter(impuesto__lte=0).aggregate(
                            tsubtotal_cero=Coalesce(Sum('subtotal'), 0),
                            tdescuento_cero=Coalesce(Sum('descuento'), 0)
                        )
                        cotizacion.subtotaliva = base_iva['tsubtotal_iva']
                        cotizacion.descuentoiva = base_cero['tdescuento_cero']
                        cotizacion.subtotalcero = base_cero['tsubtotal_cero']
                        cotizacion.descuentocero = base_iva['tdescuento_iva']
                        cotizacion.save()

                    except Exception as e:
                        raise Exception('Error en cotizacion')

                    if procesada and anulado == False:

                        if not PosAperturaCaja.objects.filter(fecha__date=fecha,cerrada=False,caja_id=caja.id).exists():
                            apertura_id = get_contador('POS_FACTURAS-APERTURA', user)
                            detalle = 'APERTURA DE CAJA [ {} ] POR EL USUARIO {}'.format(caja.codigo, user.username)
                            apertura_caja = PosAperturaCaja(
                                id=apertura_id,
                                fecha=fecha,
                                numero=apertura_id,
                                caja=caja,
                                detalle=detalle,
                                total=0,
                                cerrada=False
                            )
                            apertura_caja.save()

                        empleado = None
                        termino = parametro.codigo
                        factura_total = Decimal(dataFactura.get('total'))
                        forma_pago = dataFactura.get('formaPago','EFE')[:3]
                        termino_dias = 8

                        if termino != 'TER-CONTADO' and forma_pago != 'EFE':
                            try:
                                if cliente.empleadoid is not None and cliente.empleadoid.strip() != '':
                                    empleado = EmpEmpleados.objects.get(pk=cliente.empleadoid)
                                    if (cliente.cupo - (
                                            cliente.get_saldo_total() + empleado.get_saldo_total_empleado())) < factura_total:
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

                        tipo_factura = 'FA' if dataFactura.get('tipoDocumento','FACTURA') == 'FACTURA' else 'NV'
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
                            tipo = 'VEN-TA'
                            tarjeta = factura_total

                        if tipo_factura == 'NV':
                            try:
                                divisionid = SisDivisiones.objects.get(informal=True).id
                            except:
                                raise Exception('No se encontro division informal ID.')

                        controla_stock = False
                        try:
                            if SisParametros.objects.get(codigo='POS-MÁQUINA-SUPERMERCADO').valor.upper() == 'SI':
                                controla_stock = True
                        except:
                            pass

                        paginas = int((len(dataFactura.get('itemsOrdenes')) - 1) / items_maximo) + 1
                        lista_facturas = []

                        for i in range(paginas):
                            if contado and forma_pago == 'EFE':
                                facturaid = get_contador_sucdiv('VEN_FACTURAS-ID-', '{}{}'.format(sucursalid, divisionid[-1]))
                                if tipo_factura == 'FA':
                                    try:
                                        fact_preimpresa = get_contador_sucuencia_preimpresa(
                                            'POS-SECUENCIA-FA-{}'.format(caja.serie),
                                            caja.serie
                                        )
                                        detalle = '{} FAC:{}'.format(cliente.nombre, fact_preimpresa)
                                    except:
                                        raise Exception('No se puede generar la secuencia Factura Pre-impresa..')
                                else:
                                    fact_preimpresa = ''
                                    detalle = '{} FAC: {}'.format(cliente.nombre, facturaid)

                                factura = VenFacturas(
                                    id=facturaid,
                                    ordenid='',
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
                                    bodega_id=caja.bodega.id,
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
                                    nota=dataFactura.get('nota',''),
                                    sucursalid=sucursalid,
                                    ptg_iva=Decimal(dataFactura.get('ptg_iva',12.00)),
                                    archivo_sri=True if tipo_factura == 'FA' else False,
                                    fact_preimpresa=fact_preimpresa,
                                    efectivo=Decimal(dataFactura.get('efectivo',0)),
                                    vuelto_cliente=Decimal(dataFactura.get('vueltoCliente',0)),
                                    zona_id=cliente.zona_id if cliente.zona_id is not None else '',
                                    reimpreso=True,
                                    tipo_modelo='1',
                                    nota2=dataFactura.get('observacion','VEN-MOVIL')
                                )
                                factura.save()

                                for i in range(items_maximo):
                                    try:
                                        item = dataFactura['itemsOrdenes'].pop(0)
                                    except:
                                        break

                                    if item['cantidad'] > 0:
                                        detalleid = get_contador_sucdiv('VEN_FACTURAS_DT-ID-','{}{}'.format(sucursalid, divisionid[-1]))
                                        cantidad = round(Decimal(item['cantidad']) * Decimal(item['factor']), 2)

                                        factura_detalle = VenFacturasDetalle(
                                            id=detalleid,
                                            factura_id=factura.id,
                                            producto_id=item['productoId'],
                                            bodega_id=factura.bodega_id,
                                            cantidad=cantidad,
                                            precio=item['precio'],
                                            costo=item['costo'],
                                            subtotal=item['subtotal'],
                                            tasa_descuento=item['tasaDescuento'],
                                            descuento=item['descuento'],
                                            tasa_impuesto=item['tasaImpuesto'],
                                            impuesto=item['impuesto'],
                                            total=item['total'],
                                            empaque=item['empaque'],
                                            precio_name=item['empaque'],
                                            factor=item['factor'],
                                            sucursalid=sucursalid,
                                            clase='01'
                                        )
                                        factura_detalle.save()

                                        with connection.cursor() as cursor:
                                            cursor.execute(
                                                "{CALL INV_ProductosCardex_Insert_Pos(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                                (
                                                    factura_detalle.producto_id,
                                                    factura_detalle.bodega_id,
                                                    '',
                                                    factura.id,
                                                    factura.id,
                                                    fecha,
                                                    tipo,
                                                    detalle,
                                                    True,
                                                    factura_detalle.cantidad,
                                                    factura_detalle.costo,
                                                    divisaid,
                                                    1,
                                                    divisionid,
                                                    request.user.username,
                                                    sucursalid,
                                                    '',
                                                    caja.codigo
                                                ))

                                totales = factura.venfacturasdetalle_set.aggregate(
                                    tsubtotal=Coalesce(Sum('subtotal'), 0),
                                    tdescuento=Coalesce(Sum('descuento'), 0),
                                    timpuesto=Coalesce(Sum('impuesto'), 0),
                                    ttotal=Coalesce(Sum('total'), 0),
                                )

                                factura.subtotal = totales['tsubtotal']
                                factura.descuento = totales['tdescuento']
                                factura.impuesto = totales['timpuesto']
                                factura.total = totales['ttotal']

                                base_iva = factura.venfacturasdetalle_set.filter(impuesto__gt=0).aggregate(
                                    tsubtotal_iva=Coalesce(Sum('subtotal'), 0),
                                    tdescuento_iva=Coalesce(Sum('descuento'), 0)
                                )

                                base_cero = factura.venfacturasdetalle_set.filter(impuesto__lte=0).aggregate(
                                    tsubtotal_cero=Coalesce(Sum('subtotal'), 0),
                                    tdescuento_cero=Coalesce(Sum('descuento'), 0)
                                )

                                factura.subtotal_iva = base_iva['tsubtotal_iva']
                                factura.descuento_iva = base_cero['tdescuento_cero']
                                factura.subtotal_cero = base_cero['tsubtotal_cero']
                                factura.descuento_cero = base_iva['tdescuento_iva']
                                factura.save()

                            elif forma_pago == 'CRE':

                                asientoid = get_contador_sucdiv('ACC_ASIENTOS-ID-', '{}{}'.format(sucursalid, divisionid[-1]))
                                asiento_numero = get_contador_sucdiv('ACC_ASIENTOS-NUMBER-','{}{}'.format(sucursalid, divisionid[-1]))
                                facturaid = get_contador_sucdiv('VEN_FACTURAS-ID-', '{}{}'.format(sucursalid, divisionid[-1]))

                                if tipo_factura == 'FA':
                                    try:
                                        fact_preimpresa = get_contador_sucuencia_preimpresa(
                                            'POS-SECUENCIA-FA-{}'.format(caja.serie), caja.serie)
                                        detalle = '{} FAC:{}-{}'.format(cliente.nombre, facturaid, fecha)
                                    except:
                                        raise Exception('No se puede generar la secuencia Factura Pre-impresa..')
                                else:
                                    fact_preimpresa = ''
                                    detalle = '{} FAC:{}-'.format(cliente.nombre, facturaid, fecha)

                                try:
                                    fecha_vence = fecha + datetime.timedelta(days=termino_dias)
                                except:
                                    fecha_vence = datetime.datetime.now() + datetime.timedelta(days=termino_dias)

                                factura = VenFacturas(
                                    id=facturaid,
                                    ordenid='',
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
                                    bodega_id=caja.bodega.id,
                                    contado=contado,
                                    fecha=fecha,
                                    entregado=fecha,
                                    tipo=tipo,
                                    divisaid=divisaid,
                                    fecha_cheque=fecha,
                                    vence=fecha_vence,
                                    fecha_oc=datetime.datetime.strptime('01/01/1900', '%d/%m/%Y'),
                                    forma_pago=forma_pago,
                                    nocontrola_stock=False,
                                    nota=dataFactura.get('nota',''),
                                    sucursalid=sucursalid,
                                    ptg_iva=Decimal(dataFactura.get('ptg_iva',12.00)),
                                    archivo_sri=True if tipo_factura == 'FA' else False,
                                    fact_preimpresa=fact_preimpresa,
                                    zona_id=cliente.zona_id if cliente.zona_id is not None else '',
                                    credito=credito,
                                    dias_credito=termino_dias if termino_dias > 0 else 8,
                                    reimpreso=True,
                                    tipo_modelo='1',
                                    nota2=dataFactura.get('observacion','VEN-MOVIL')
                                )
                                factura.save()

                                for i in range(items_maximo):
                                    try:
                                        item = dataFactura['items'].pop(0)
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
                                            clase='01'
                                        )
                                        factura_detalle.save()

                                        with connection.cursor() as cursor:
                                            cursor.execute(
                                                "{CALL INV_ProductosCardex_Insert_Pos(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                                (
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
                                                    '',
                                                    caja.codigo
                                                ))

                                totales = factura.venfacturasdetalle_set.aggregate(
                                    tsubtotal=Coalesce(Sum('subtotal'), 0),
                                    tdescuento=Coalesce(Sum('descuento'), 0),
                                    timpuesto=Coalesce(Sum('impuesto'), 0),
                                    ttotal=Coalesce(Sum('total'), 0),
                                )

                                factura.subtotal = totales['tsubtotal']
                                factura.descuento = totales['tdescuento']
                                factura.impuesto = totales['timpuesto']
                                factura.total = totales['ttotal']

                                base_iva = factura.venfacturasdetalle_set.filter(impuesto__gt=0).aggregate(
                                    tsubtotal_iva=Coalesce(Sum('subtotal'), 0),
                                    tdescuento_iva=Coalesce(Sum('descuento'), 0)
                                )

                                base_cero = factura.venfacturasdetalle_set.filter(impuesto__lte=0).aggregate(
                                    tsubtotal_cero=Coalesce(Sum('subtotal'), 0),
                                    tdescuento_cero=Coalesce(Sum('descuento'), 0)
                                )

                                factura.subtotal_iva = base_iva['tsubtotal_iva']
                                factura.descuento_iva = base_cero['tdescuento_cero']

                                factura.subtotal_cero = base_cero['tsubtotal_cero']
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
                                cta_descuentos = factura.venfacturasdetalle_set.values(
                                    ctadescuento=Max('producto__ctadescuento')
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

                                cta_costos = factura.venfacturasdetalle_set.values(
                                    ctacostos=Max('producto__ctacostos'),
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
                                    raise Exception('Asiento desbalanceado. TOTAL DEBE:{}  TOTAL HABER:{}'.format(total_debe, total_haber))

                                if cliente.empleadoid is not None and empleado is not None:
                                    emleado_deudaid = get_contador_sucdiv('EMP_EMPLEADOS_DEUDAS-ID-','{}{}'.format(sucursalid, divisionid[-1]))
                                    with connection.cursor() as cursor:
                                        valor_base = round(factura.total * Decimal(1.00), 2)
                                        cursor.execute("{CALL EMP_EmpleadosDeudas_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
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
                                    cliente_deudaid = get_contador_sucdiv('CLI_CLIENTES_DEUDAS-ID-',
                                                                          '{}{}'.format(sucursalid, divisionid[-1]))

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
                                'tipo': tipo_factura,
                            })

                        data['tipo'] = tipo_factura
                        data['documentos'] = lista_facturas
                    data['resp'] = True
                    return Response(data, status=200)

        except Exception as e:
            data['error'] = str(e)
            data['resp'] = False
        return Response(data, status=200)
