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
from cliente.models import CliClientes, CliCotizaciones, CliCotizacionesDetalle, CliRubros
from contabilidad.models import AccAsientos
from contadores.fn_contador import get_contador, get_contador_sucdiv, get_contador_sucuencia_preimpresa
from empleado.models import EmpEmpleados, EmpRubros
from pos.models import PosAperturaCaja
from seguridad.models import SegUsuarioParametro
from sistema.constantes import USER_ALL_PERMISOS
from sistema.funciones import addUserData
from sistema.models import SisSucursales, SisParametros, SisDivisiones
from venta.models import VenFacturas, VenFacturasDetalle

class PosAperturaCierreCaja(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        try:
            accion = request.POST.get('accion')
            if accion == 'pos-aperturar-caja':
                with transaction.atomic():
                    valor = Decimal(request.POST.get('valor', '0.01'))
                    user = request.user
                    apertura_id = get_contador('POS_FACTURAS-APERTURA', user)
                    caja = user.segusuarioparametro.caja
                    detalle = 'APERTURA DE CAJA [ {} ] POR EL USUARIO {}'.format(caja.codigo, user.username)

                    apertura_caja = PosAperturaCaja(
                        id=apertura_id,
                        fecha=datetime.datetime.strptime(request.POST.get('fecha'), '%d/%m/%Y'),
                        numero=apertura_id,
                        caja=caja,
                        detalle=detalle,
                        total=round(valor, 2),
                        cerrada=False
                    )
                    apertura_caja.save()
                    data['resp'] = True
                    return JsonResponse(data, status=200)
        except Exception as e:
            data['error'] = 'error: ' + str(e)
        return JsonResponse(data, status=200)

    def get(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        try:
            accion = request.GET.get('accion')
            if accion == 'pos-apertura-caja':
                fecha = datetime.datetime.strptime(request.GET.get('fecha'), '%d/%m/%Y')
                caja_id = request.GET.get('caja_id')
                if PosAperturaCaja.objects.filter(cerrada=False, fecha__date=fecha, caja_id=caja_id).exists():
                    data['aperturado'] = True
                else:
                    data['aperturado'] = False
                data['resp'] = True
                return JsonResponse(data, status=200)
        except Exception as e:
            data['error'] = 'error: ' + str(e)
        return JsonResponse(data, status=200)

class PosPuntoVentaFactura(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        try:
            accion = request.POST.get('accion')
            if accion == 'cotizacion-add-item':
                with transaction.atomic():

                    json_data = json.loads(request.POST['cotizacion'])
                    cotizacion_id = request.POST.get('cotizacion_id')
                    cotizacion = CliCotizaciones.objects.filter(pk=cotizacion_id, anulado=False).first()
                    fecha = datetime.datetime.strptime(json_data['fecha'], '%d/%m/%Y')
                    user = request.user
                    if cotizacion is None:
                        sucursalid = json_data['sucursalid']
                        divisionid = json_data['divisionid']
                        divisaid = json_data['divisaid']
                        cotizacion_id = get_contador('CLI_COTIZACIONES-ID',user)
                        cotizacion_numero = get_contador('CLI_COTIZACIONES-NUMBER',user)

                        cotizacion = CliCotizaciones(
                            id=cotizacion_id,
                            numero=cotizacion_numero,
                            tipo='COT-FA',
                            fecha=fecha,
                            cliente_id=json_data['clienteid'],
                            nombre=json_data['nombre'],
                            vendedor_id=json_data['vendedorid'],
                            divisaid=divisaid,
                            cambio=Decimal('1.00'),
                            atentamente=user.username,
                            validez='15 DIAS',
                            terminoid=json_data['terminoid'],
                            detalle='Pendiente Doc: {}'.format(json_data['nombre']),
                            division=divisionid,
                            sucursalid=sucursalid,
                            caja_id=json_data['cajaid'],
                            caja_code=json_data['caja_code'],
                            contado=json_data['contado'],
                            empleadoid=json_data['empleadoid'],
                            bodega_id=json_data['bodegaid'],
                            entregado=fecha,

                            subtotal=Decimal(json_data['subtotal']),
                            descuento=Decimal(json_data['descuento']),
                            impuesto=Decimal(json_data['impuesto']),
                            total=Decimal(json_data['total']),
                            subtotalcero=Decimal(json_data['base_tarifa_cero']),
                            subtotaliva=Decimal(json_data['base_tarifa_iva']),
                            descuentocero=Decimal(json_data['base_descuento_cero']),
                            descuentoiva=Decimal(json_data['base_descuento_iva'])
                        )
                        cotizacion.save()
                    else:
                        cotizacion.fecha = fecha,
                        cotizacion.cliente_id = json_data['clienteid']
                        cotizacion.nombre = json_data['nombre']
                        cotizacion.vendedor_id = json_data['vendedorid']
                        cotizacion.contado = json_data['contado']
                        cotizacion.terminoid = json_data['terminoid']

                        cotizacion.subtotal = Decimal(json_data['subtotal'])
                        cotizacion.descuento = Decimal(json_data['descuento'])
                        cotizacion.impuesto = Decimal(json_data['impuesto'])
                        cotizacion.total = Decimal(json_data['total'])
                        cotizacion.subtotalcero = Decimal(json_data['base_tarifa_cero'])
                        cotizacion.subtotaliva = Decimal(json_data['base_tarifa_iva'])
                        cotizacion.descuentocero = Decimal(json_data['base_descuento_cero'])
                        cotizacion.descuentoiva = Decimal(json_data['base_descuento_iva'])

                    cotizacion_dt_id = get_contador('CLI_COTIZACIONES_DT-ID', user)
                    item = json_data['item']
                    cotizacion_detalle = CliCotizacionesDetalle(
                        id=cotizacion_dt_id,
                        cotizacion_id=cotizacion.id,
                        producto_id=item['productoid'],
                        nombre=item['nombre'],
                        bodegaid=cotizacion.bodega_id,
                        codigo=item['codigo'],
                        cantidad=item['cantidad'],
                        precio=item['precio'],
                        precio_display=item['precio_display'],
                        precio_factor=item['precio_factor'],
                        precio_final=item['precio_final'],
                        costo=item['costo_compra'],
                        subtotal=item['subtotal'],
                        tasa_descuento=item['tasa_descuento'],
                        descuento=item['descuento'],
                        impuestoid=item['impuestoid'],
                        tasa_impuesto=item['tasaimpuesto'],
                        impuesto=item['impuesto'],
                        total=item['total'],
                        empaque=item['empaque'],
                        factor=item['factor'],
                        sucursalid=json_data['sucursalid'],
                        clase=item['clase'],
                        valor_comision=item['valor_comision'],
                        comision_contado=item['comision_contado'],
                        comision_credito=item['comision_credito'],
                        coniva=item['coniva']
                    )
                    cotizacion_detalle.save()
                    data['cotizacion'] = {
                        'id':cotizacion.id,
                        'numero': cotizacion.numero
                    }
                    data['resp'] = True
                    return JsonResponse(data, status=200)
            if accion == 'cotizacion-edit-item':
                with transaction.atomic():
                    json_data = json.loads(request.POST['cotizacion'])
                    cotizacion_id = request.POST.get('cotizacion_id')
                    cotizacion = CliCotizaciones.objects.filter(pk=cotizacion_id, anulado=False).first()
                    if cotizacion is not None:
                        item = json_data['item']
                        cd = cotizacion.clicotizacionesdetalle_set.filter(anulado=False,codigo=item['codigo'],producto_id=item['productoid']).first()
                        if cd is not None:
                            cd.cantidad = item['cantidad']
                            cd.precio = item['precio']
                            cd.precio_display = item['precio_display']
                            cd.precio_factor = item['precio_factor']
                            cd.precio_final = item['precio_final']
                            cd.costo = item['costo_compra']
                            cd.subtotal = item['subtotal']
                            cd.tasa_descuento = item['tasa_descuento']
                            cd.descuento = item['descuento']
                            cd.impuestoid = item['impuestoid']
                            cd.tasa_impuesto = item['tasaimpuesto']
                            cd.impuesto = item['impuesto']
                            cd.total = item['total']
                            cd.empaque = item['empaque']
                            cd.factor = item['factor']
                            cd.sucursalid = json_data['sucursalid']
                            cd.clase = item['clase']
                            cd.valor_comision = item['valor_comision']
                            cd.comision_contado = item['comision_contado']
                            cd.comision_credito = item['comision_credito']
                            cd.coniva = item['coniva']
                            cd.save()

                        cotizacion.subtotal = Decimal(json_data['subtotal'])
                        cotizacion.descuento = Decimal(json_data['descuento'])
                        cotizacion.impuesto = Decimal(json_data['impuesto'])
                        cotizacion.total = Decimal(json_data['total'])
                        cotizacion.subtotalcero = Decimal(json_data['base_tarifa_cero'])
                        cotizacion.subtotaliva = Decimal(json_data['base_tarifa_iva'])
                        cotizacion.descuentocero = Decimal(json_data['base_descuento_cero'])
                        cotizacion.descuentoiva = Decimal(json_data['base_descuento_iva'])
                        cotizacion.save()
                        data['cotizacion'] = {
                            'id':cotizacion.id,
                            'numero': cotizacion.numero
                        }
                        data['resp'] = True
                        return JsonResponse(data, status=200)
                    raise Exception('No se encontro item producto..')
            if accion == 'cotizacion-delete-item':
                with transaction.atomic():
                    codigo_acceso = request.POST.get('codigo_acceso')
                    if SegUsuarioParametro.objects.filter(activo=True,codigo_acceso=codigo_acceso).exists():
                        json_data = json.loads(request.POST['cotizacion'])
                        cotizacion_id = request.POST.get('cotizacion_id')
                        anuladopor = request.POST.get('anuladopor',self.request.user.username)
                        #usuario_id = request.POST.get('usuario_id',self.request.user.id)

                        cotizacion = CliCotizaciones.objects.filter(pk=cotizacion_id, anulado=False).first()
                        if cotizacion is not None:
                            item = json_data['item']
                            if item['accion'] == 'ALL':
                                cotizacion.clicotizacionesdetalle_set.update(anulado=True,anuladopor=anuladopor)
                            else:
                                cotizacion.clicotizacionesdetalle_set.filter(
                                    codigo=item['codigo'],
                                    producto_id=item['productoid']
                                ).update(anulado=True,anuladopor=anuladopor)

                            cotizacion.subtotal = Decimal(json_data['subtotal'])
                            cotizacion.descuento = Decimal(json_data['descuento'])
                            cotizacion.impuesto = Decimal(json_data['impuesto'])
                            cotizacion.total = Decimal(json_data['total'])
                            cotizacion.subtotalcero = Decimal(json_data['base_tarifa_cero'])
                            cotizacion.subtotaliva = Decimal(json_data['base_tarifa_iva'])
                            cotizacion.descuentocero = Decimal(json_data['base_descuento_cero'])
                            cotizacion.descuentoiva = Decimal(json_data['base_descuento_iva'])
                            cotizacion.save()

                        data['cotizacion'] = {
                            'id':cotizacion.id,
                            'numero': cotizacion.numero
                        }
                        data['resp'] = True
                        return JsonResponse(data, status=200)
                    else:
                        raise Exception('No cuenta con autorizacion para eliminar Items..')
            elif accion == 'guadar-factura':

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

                    if termino != 'TER-CONTADO' and forma_pago != 'EFE':
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
                                tipo_modelo='1',
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
                                        cursor.execute("{CALL INV_ProductosCardex_Insert_Pos(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
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
                                            '',
                                            caja.codigo
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
                                tipo_modelo='1',
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
                                        cursor.execute("{CALL INV_ProductosCardex_Insert_Pos(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
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
                            CliCotizaciones.objects.filter(pk=cotizacionid).update(anulado=True)
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
        data = {}
        addUserData(request, data)
        try:
            data['user_parametro'] = user_parametro = request.user.segusuarioparametro
            caja = user_parametro.caja
            if caja is None:
                raise Exception('No se encontro caja asociado al usuario..')
            try:
                data['cliente'] = cliente = CliClientes.objects.get(id='0000000001', anulado=False)
                data['termino'] = SisParametros.objects.get(pk=cliente.termino)
                data['empleado'] = user_parametro.empleado
            except:
                data['cliente'] = None
                data['empleado'] = None

            data['caja'] = caja
            data['sucursal'] = SisSucursales.objects.get(codigo=caja.sucursal)

            if caja.bodega is not None:
                data['bodega'] = caja.bodega

            parametro = SisParametros.objects.get(codigo='IMPUESTO-IVA')
            data['tasa_impuesto'] = Decimal(parametro.valor.strip())
            data['cta_impuestoid'] = parametro.extradata.strip().replace('CuentaID=', '')
            data['vendedores'] = EmpEmpleados.objects.filter(anulado=False, funcion__codigo='101')

            try:
                parametro = SisParametros.objects.get(codigo='POS-MÁQUINA-SUPERMERCADO')
                data['controla_stock'] = 0 if parametro.valor.upper() == 'SI' else 1
            except:
                data['controla_stock'] = 0

            if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                data['disabled'] = True
            return render(request, 'pos/pos_punto_venta_factura.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')


class PosPuntoVentaFacturaMovil(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        data = {}
        addUserData(request, data)
        try:
            data['user_parametro'] = user_parametro = request.user.segusuarioparametro
            caja = user_parametro.caja
            if caja is None:
                raise Exception('No se encontro caja asociado al usuario..')
            try:
                data['cliente'] = cliente = CliClientes.objects.get(id='0000000001', anulado=False)
                data['termino'] = SisParametros.objects.get(pk=cliente.termino)
                data['empleado'] = user_parametro.empleado
            except:
                data['cliente'] = None
                data['empleado'] = None

            data['caja'] = caja
            data['sucursal'] = SisSucursales.objects.get(codigo=caja.sucursal)

            if caja.bodega is not None:
                data['bodega'] = caja.bodega

            parametro = SisParametros.objects.get(codigo='IMPUESTO-IVA')
            data['tasa_impuesto'] = Decimal(parametro.valor.strip())
            data['cta_impuestoid'] = parametro.extradata.strip().replace('CuentaID=', '')
            data['vendedores'] = EmpEmpleados.objects.filter(anulado=False, funcion__codigo='101')

            try:
                parametro = SisParametros.objects.get(codigo='POS-MÁQUINA-SUPERMERCADO')
                data['controla_stock'] = 0 if parametro.valor.upper() == 'SI' else 1
                parametro = SisParametros.objects.get(codigo='WEB-CON-COTIZACION')
                data['con_cotizacion'] = True if parametro.valor.upper() == 'SI' else False
            except:
                data['controla_stock'] = 0
                data['con_cotizacion'] = False

            if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                data['disabled'] = True
            return render(request, 'pos/pos_punto_venta_movil.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')
