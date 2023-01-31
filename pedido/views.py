import datetime
import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.generic.base import View

from banco.models import BanBancos
from cliente.models import CliClientes
from empleado.models import EmpEmpleados
from inventario.models import InvPdBodegaStock
from pedido.models import VenOrdenPedidos, VenOrdenPedidosDetalle
from sistema.constantes import USER_ALL_PERMISOS, ESTADO_ORDEN_PEDIDO, PEDIDOS_CONTROLA_STOCK
from sistema.funciones import addUserData
from sistema.models import SisParametros, SisSucursales, SisDivisiones

class InformeOrdenesPedidosView(LoginRequiredMixin,ListView):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    model = VenOrdenPedidos
    template_name = 'pedido/ped_informe_pedidos.html'  # Default: <app_label>/<model_name>_list.html
    context_object_name = 'ordenes'  # Default: object_list
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
          s,inicio, final,divisionid,vendedorid,self.creadopor,estado_pedido
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
        context['vendedores'] = EmpEmpleados.objects.filter(anulado=False,vendedor=True)
        context['estado_pedidos'] = ESTADO_ORDEN_PEDIDO

        if self.request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
            context['permiso'] = True

        return context

    def get_queryset(self, **kwargs):
        search = self.request.GET.get('s', '')
        criterio = {
            'division_id': self.request.GET.get('divisionid', ''),
            'vendedor_id': self.request.GET.get('vendedorid', ''),
            'creadopor': self.request.GET.get('creadopor', ''),
            'estado': self.request.GET.get('estado_pedido', '')
        }
        if not self.request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
            criterio['creadopor'] = self.request.user.username
            self.disabled = True

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
            Q(cliente__ruc__icontains=search) |
            Q(cliente__nombre__icontains=search),
            *queries(criterio)
        )

class OrdenPedidoVenta(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        accion = request.POST['accion']
        try:
            if accion == 'orden_pedido_crear':

                with transaction.atomic():
                    json_data = json.loads(request.POST['pedido'])
                    cliente = json_data['cliente']
                    fecha = datetime.datetime.strptime(json_data['fecha'], '%d/%m/%Y')

                    pedido = VenOrdenPedidos(
                        cliente_id=json_data['clienteid'],
                        detalle=cliente['nombre'],
                        ruc=cliente['ruc'],
                        empleadoid=json_data['empleadoid'],
                        vendedor_id=cliente['vendedorid'],
                        caja_id=json_data['cajaid'],
                        terminoid=cliente['terminoid'],
                        division_id=json_data['divisionid'],
                        bodega_id=json_data['bodegaid'],
                        contado=json_data['contado'],
                        fecha=fecha,
                        entregado=datetime.datetime.strptime(json_data['fecha_entrega'], '%d/%m/%Y'),
                        tipo=json_data['tipo'],
                        divisaid=json_data['divisaid'],
                        cambio=Decimal('1.00'),
                        subtotal=Decimal(json_data['subtotal']),
                        descuento=Decimal(json_data['descuento']),
                        impuesto=Decimal(json_data['impuesto']),
                        total=Decimal(json_data['total']),
                        costo_total=Decimal(json_data['total']),
                        total_comision=Decimal(json_data['total_comision']),
                        zona_id=cliente['zona_id'],
                        nota=json_data['nota'],
                        sucursalid=json_data['sucursalid'],
                        subtotal_cero=json_data['base_tarifa_cero'],
                        subtotal_iva=json_data['base_tarifa_iva'],
                    )
                    pedido.save()

                    for item in json_data['items']:
                        if item['cantidad'] > 0:
                            pedido_detalle = VenOrdenPedidosDetalle(
                                orden_pedido_id=pedido.id,
                                producto_id=item['productoid'],
                                bodega_id=pedido.bodega_id,
                                codigo=item['codigo'],
                                cantidad=item['cantidad'],
                                precio=item['precio'],
                                precio_display=item['precio_display'],
                                precio_factor=item['precio_factor'],
                                precio_final=item['precio_final'],
                                costo=item['costo_compra'],
                                ctacosto_id=item['ctacosto_id'],
                                ctadescuento_id=item['ctadescuento_id'],
                                ctadevolucion_id=item['ctadevolucion_id'],
                                ctaimpuestoid=item['ctaimpuestoid'],
                                ctamayor_id=item['ctamayor_id'],
                                ctaventa_id=item['ctaventa_id'],
                                subtotal=item['subtotal'],
                                tasa_descuento=item['tasadescuento'],
                                descuento=item['descuento'],
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
                            pedido_detalle.save()

                            stock = 0
                            producto_stock = pedido_detalle.producto.get_bodega_stock(pedido.bodega_id,pedido.sucursalid)
                            if producto_stock is not None:
                                stock = producto_stock['stock']

                            if stock <= 0:
                                raise Exception("El producto {}:{} se encuentra SIN Stock en bodega: {}-{}".format(
                                    pedido_detalle.producto.codigo,
                                    pedido_detalle.producto.nombre_corto,
                                    pedido_detalle.bodega.codigo,
                                    pedido_detalle.bodega.nombre)
                                )
                            elif (pedido_detalle.cantidad * pedido_detalle.factor) > stock:
                                raise Exception("La cantidad del producto {}:{} supera el stock: {} : {}".format(pedido_detalle.producto.codigo,pedido_detalle.producto.nombre_corto,stock,pedido.bodega.nombre))

                            try:
                                pbodega = InvPdBodegaStock.objects.get(
                                    producto_id=item['productoid'],
                                    bodega_id=pedido.bodega_id,
                                    bodega__sucursal=pedido.sucursalid
                                )
                                pbodega.stock_reservado = round(pbodega.stock_reservado,2) + round(Decimal(item['cantidad']) * Decimal(item['factor']),2)
                                pbodega.save()
                            except:
                                raise Exception('Error en actualizar el Stock Reservado en bodega: {}'.format(pedido.bodega.nombre))

                    data['resp'] = True
                    return JsonResponse(data, status=200)

            elif accion == 'orden_pedido_editar':

                with transaction.atomic():
                    json_data = json.loads(request.POST['pedido'])
                    try:
                        pedido = VenOrdenPedidos.objects.get(pk=json_data['pedidoid'])
                    except:
                        raise Exception("No se encontro la orden de pedido.")

                    if pedido.estado == '5'.strip():
                        raise Exception("No se permite editar un pedido facturado.")

                    cliente = json_data['cliente']
                    fecha = datetime.datetime.strptime(json_data['fecha'], '%d/%m/%Y')

                    pedido.cliente_id=json_data['clienteid']
                    pedido.detalle=cliente['nombre']
                    pedido.ruc=cliente['ruc']
                    pedido.empleadoid=json_data['empleadoid']
                    pedido.vendedor_id=cliente['vendedorid']
                    pedido.caja_id=json_data['cajaid']
                    pedido.terminoid=cliente['terminoid']
                    pedido.division_id=json_data['divisionid']
                    pedido.bodega_id=json_data['bodegaid']
                    pedido.contado=json_data['contado']
                    pedido.fecha=fecha
                    pedido.entregado=fecha
                    pedido.tipo=json_data['tipo']
                    pedido.divisaid=json_data['divisaid']
                    pedido.cambio=Decimal('1.00')
                    pedido.subtotal=Decimal(json_data['subtotal'])
                    pedido.descuento=Decimal(json_data['descuento'])
                    pedido.impuesto=Decimal(json_data['impuesto'])
                    pedido.total=Decimal(json_data['total'])
                    pedido.costo_total=Decimal(json_data['total'])
                    pedido.total_comision=Decimal(json_data['total_comision'])
                    pedido.zona_id=cliente['zona_id']
                    pedido.nota=json_data['nota']
                    pedido.sucursalid=json_data['sucursalid']
                    pedido.subtotal_cero=json_data['base_tarifa_cero']
                    pedido.subtotal_iva=json_data['base_tarifa_iva']
                    pedido.estado = '1'
                    pedido.save()

                    productos_codigos = [e['codigo'] for e in json_data['items']]

                    for item in pedido.venordenpedidosdetalle_set.exclude(
                            codigo__in=productos_codigos
                        ):
                        try:
                            pbodega = InvPdBodegaStock.objects.get(
                                producto_id=item.producto_id,
                                bodega_id=pedido.bodega_id,
                                bodega__sucursal=pedido.sucursalid
                            )
                            pbodega.stock_reservado = round(pbodega.stock_reservado, 2) - round(Decimal(item.cantidad) * Decimal(item.factor), 2)
                            pbodega.save()
                        except:
                            raise Exception('Error en actualizar el Stock Reservado en bodega: {}'.format(pedido.bodega.nombre))

                    pedido.venordenpedidosdetalle_set.exclude(codigo__in=productos_codigos).delete()

                    for item in json_data['items']:
                        if Decimal(item['cantidad']) > 0:

                            pedido_detalles = VenOrdenPedidosDetalle.objects.filter(orden_pedido_id=pedido.id,codigo=item['codigo'],producto_id=item['productoid'])
                            if pedido_detalles.exists():

                                pedido_detalle = pedido_detalles[0]
                                cantidad_ant = round(pedido_detalle.cantidad,2)

                                pedido_detalle.bodega_id = pedido.bodega_id
                                pedido_detalle.cantidad = round(item['cantidad'],2)
                                pedido_detalle.precio = item['precio']
                                pedido_detalle.precio_display = item['precio_display']
                                pedido_detalle.precio_factor = item['precio_factor']
                                pedido_detalle.precio_final = item['precio_final']
                                pedido_detalle.costo = item['costo_compra']
                                pedido_detalle.ctacosto_id = item['ctacosto_id']
                                pedido_detalle.ctadescuento_id = item['ctadescuento_id']
                                pedido_detalle.ctadevolucion_id = item['ctadevolucion_id']
                                pedido_detalle.ctaimpuestoid = item['ctaimpuestoid']
                                pedido_detalle.ctamayor_id = item['ctamayor_id']
                                pedido_detalle.ctaventa_id = item['ctaventa_id']
                                pedido_detalle.subtotal = item['subtotal']
                                pedido_detalle.tasa_descuento = item['tasadescuento']
                                pedido_detalle.descuento = item['descuento']
                                pedido_detalle.tasa_impuesto = item['tasaimpuesto']
                                pedido_detalle.impuesto = item['impuesto']
                                pedido_detalle.total = item['total']
                                pedido_detalle.empaque = item['empaque']
                                pedido_detalle.factor = item['factor']
                                pedido_detalle.sucursalid = json_data['sucursalid']
                                pedido_detalle.clase = item['clase']
                                pedido_detalle.valor_comision = item['valor_comision']
                                pedido_detalle.comision_contado = item['comision_contado']
                                pedido_detalle.comision_credito = item['comision_credito']
                                pedido_detalle.coniva = item['coniva']
                                pedido_detalle.save()

                                if round(pedido_detalle.cantidad,2) != cantidad_ant:
                                    try:
                                        pbodega = InvPdBodegaStock.objects.get(
                                            producto_id=item['productoid'],
                                            bodega_id=pedido.bodega_id,
                                            bodega__sucursal=pedido.sucursalid
                                        )
                                        if pedido_detalle.cantidad > cantidad_ant:
                                            reservado = pedido_detalle.cantidad - cantidad_ant

                                            stock = 0
                                            producto_stock = pedido_detalle.producto.get_bodega_stock(pedido.bodega_id,pedido.sucursalid)
                                            if producto_stock is not None:
                                                stock = producto_stock['stock']
                                            if stock <= 0:
                                                raise Exception(
                                                    "El producto {}:{} se encuentra SIN Stock en bodega: {}-{}".format(
                                                        pedido_detalle.producto.codigo,
                                                        pedido_detalle.producto.nombre_corto,
                                                        pedido_detalle.bodega.codigo,
                                                        pedido_detalle.bodega.nombre)
                                                )
                                            elif (reservado * pedido_detalle.factor) > stock:
                                                raise Exception("La cantidad del producto {}:{} supera el stock: {} : {}".format(
                                                        pedido_detalle.producto.codigo,
                                                        pedido_detalle.producto.nombre_corto, stock,
                                                        pedido.bodega.nombre))

                                            pbodega.stock_reservado = round(pbodega.stock_reservado, 2) + round(Decimal(reservado) * Decimal(item['factor']), 2)

                                        else:

                                            reservado = cantidad_ant - pedido_detalle.cantidad
                                            pbodega.stock_reservado = round(pbodega.stock_reservado, 2) - round(Decimal(reservado) * Decimal(item['factor']), 2)

                                        pbodega.save()

                                    except:
                                        raise Exception('Error en actualizar el Stock Reservado en bodega: {}'.format(pedido.bodega.nombre))

                            else:
                                pedido_detalle = VenOrdenPedidosDetalle(
                                    orden_pedido_id=pedido.id,
                                    producto_id=item['productoid'],
                                    bodega_id=pedido.bodega_id,
                                    codigo=item['codigo'],
                                    cantidad=item['cantidad'],
                                    precio=item['precio'],
                                    precio_display=item['precio_display'],
                                    precio_factor=item['precio_factor'],
                                    precio_final=item['precio_final'],
                                    costo=item['costo_compra'],
                                    ctacosto_id=item['ctacosto_id'],
                                    ctadescuento_id=item['ctadescuento_id'],
                                    ctadevolucion_id=item['ctadevolucion_id'],
                                    ctaimpuestoid=item['ctaimpuestoid'],
                                    ctamayor_id=item['ctamayor_id'],
                                    ctaventa_id=item['ctaventa_id'],
                                    subtotal=item['subtotal'],
                                    tasa_descuento=item['tasadescuento'],
                                    descuento=item['descuento'],
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
                                pedido_detalle.save()

                                stock = 0
                                producto_stock = pedido_detalle.producto.get_bodega_stock(pedido.bodega_id,pedido.sucursalid)
                                if producto_stock is not None:
                                    stock = producto_stock['stock']
                                if stock <= 0:
                                    raise Exception("El producto {}:{} se encuentra SIN Stock en bodega: {}-{}".format(
                                        pedido_detalle.producto.codigo,
                                        pedido_detalle.producto.nombre_corto,
                                        pedido_detalle.bodega.codigo,
                                        pedido_detalle.bodega.nombre)
                                    )
                                elif (pedido_detalle.cantidad * pedido_detalle.factor) > stock:
                                    raise Exception("La cantidad del producto {}:{} supera el stock: {} : {}".format(
                                        pedido_detalle.producto.codigo,
                                        pedido_detalle.producto.nombre_corto,
                                        stock,
                                        pedido.bodega.nombre)
                                    )
                                try:
                                    pbodega = InvPdBodegaStock.objects.get(
                                        producto_id=item['productoid'],
                                        bodega_id=pedido.bodega_id,
                                        bodega__sucursal=pedido.sucursalid
                                    )
                                    pbodega.stock_reservado = round(pbodega.stock_reservado, 2) + round(Decimal(item['cantidad']) * Decimal(item['factor']), 2)
                                    pbodega.save()
                                except:
                                    raise Exception('Error en actualizar el Stock Reservado en bodega: {}'.format(pedido.bodega.nombre))

                    data['resp'] = True
                    return JsonResponse(data, status=200)

        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, status=200)

    def get(self, request, *args, **kwargs):
        data = {"editar":False}
        addUserData(request, data)
        try:
            pedido_id = kwargs.get("pk", None)
            if pedido_id is not None:

                data['accion'] = 'orden_pedido_editar'
                data['editar'] = True
                try:
                    pedido = VenOrdenPedidos.objects.get(pk=pedido_id)
                except:
                    raise Exception("No se encontro la orden de pedido.")

                if pedido.estado == '5'.strip():
                    raise Exception("No se permite editar un pedido facturado.")

                if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                    if pedido.creadopor.strip().upper() != request.user.username.strip().upper():
                        raise Exception("No se permite editar el pedido para el usuario actual..")

                data['pedido'] = pedido
                data['fecha'] = pedido.fecha
                data['fecha_entrega'] = pedido.entregado
                caja = pedido.caja
                if caja is None:
                    raise Exception('No se encontro caja asociado al usuario..')
                try:
                    data['cliente'] = pedido.cliente
                    data['empleado'] = request.user.segusuarioparametro.empleado
                except:
                    data['cliente'] = None
                    data['empleado'] = None

                data['caja_id'] = caja.id
                data['sucursal'] = pedido.sucursalid

                if caja.bodega is not None:
                    data['bodega'] = caja.bodega

            else:
                data['accion'] = 'orden_pedido_crear'
                data['fecha'] = data['hoy']
                data['fecha_entrega'] = data['hoy']
                caja = request.user.segusuarioparametro.caja
                if caja is None:
                    raise Exception('No se encontro caja asociado al usuario..')
                try:
                    data['cliente'] = CliClientes.objects.get(id='0000000001', anulado=False)
                    data['empleado'] = request.user.segusuarioparametro.empleado
                except:
                    data['cliente'] = None
                    data['empleado'] = None

                data['caja_id'] = caja.id
                data['sucursal'] = SisSucursales.objects.get(codigo=caja.sucursal)

                if caja.bodega is not None:
                    data['bodega'] = caja.bodega

            parametro = SisParametros.objects.get(codigo='IMPUESTO-IVA')
            data['tasa_impuesto'] = Decimal(parametro.valor.strip())
            data['cta_impuestoid'] = parametro.extradata.strip().replace('CuentaID=', '')

            if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                data['disabled'] = True

            return render(request, 'pedido/orden_pedido.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')

class OrdenPedidoPuntoVenta(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        accion = request.POST['accion']
        try:
            if accion == 'orden_pedido_crear':
                with transaction.atomic():
                    try:
                        cliente = CliClientes.objects.get(pk=request.POST.get('cliente_id'))
                    except:
                        raise Exception('No se encontro cliente seleccionado..')

                    if cliente.id == '0000000001' or cliente.nombre == 'CONSUMIDOR FINAL':
                        raise Exception('No se permite facturar a consumidor final..')

                    try:
                        caja = BanBancos.objects.get(pk=request.POST.get('caja_id'))
                    except:
                        raise Exception('No se encontro caja banco..')

                    #factura_total = Decimal(request.POST.get('factura_total', 0))
                    termino = request.POST.get('termino')
                    forma_pago = request.POST.get('forma_pago')
                    termino_dias = 0

                    if termino != 'TER-CONTADO' and forma_pago == 'CRE':
                        # try:
                        #     if cliente.empleadoid is not None and cliente.empleadoid.strip() != '':
                        #         empleado = EmpEmpleados.objects.get(pk=cliente.empleadoid)
                        #         if (cliente.cupo - (cliente.get_saldo_total() + empleado.get_saldo_total_empleado())) < factura_total:
                        #             #raise Exception('La orden excede el cupo disponible del Cliente.')
                        #             mensaje = 'La orden excede el cupo disponible del Cliente.'
                        #     else:
                        #         if (cliente.cupo - cliente.get_saldo_total()) < factura_total:
                        #             mensaje = 'La orden excede el cupo disponible del Cliente.'
                        #             #raise Exception('La orden excede el cupo disponible del Cliente.')
                        # except:
                        #     mensaje = 'No se pudo determinar el cupo disponible del Cliente'
                        #     #raise Exception('No se pudo determinar el cupo disponible del Cliente')

                        try:
                            termino_dias = int(SisParametros.objects.get(pk=cliente.termino).valor)
                        except:
                            termino_dias = 4

                    json_data = json.loads(request.POST['pedido'])
                    fecha = datetime.datetime.strptime(json_data['fecha'], '%d/%m/%Y')
                    contado = bool(int(request.POST.get('contado')))

                    divisaid = json_data['divisaid']
                    sucursalid = json_data['sucursalid']
                    divisionid = json_data['divisionid']

                    try:
                        fecha_vence = fecha + datetime.timedelta(days=termino_dias)
                    except:
                        fecha_vence = datetime.datetime.now() + datetime.timedelta(days=termino_dias)

                    pedido = VenOrdenPedidos(
                        cliente_id=cliente.id,
                        detalle=cliente.nombre,
                        ruc=cliente.ruc,
                        empleadoid=cliente.empleadoid,
                        vendedor_id=cliente.vendedor_id,
                        caja_id=caja.id,
                        terminoid=cliente.termino,
                        division_id=divisionid,
                        bodega_id=json_data['bodegaid'],
                        contado=contado,
                        fecha=fecha,
                        entregado=datetime.datetime.strptime(json_data['fecha_entrega'], '%d/%m/%Y'),
                        tipo=json_data['tipo'],
                        divisaid=divisaid,
                        forma_pago=forma_pago,
                        subtotal=json_data['subtotal'],
                        descuento=json_data['descuento'],
                        impuesto=json_data['impuesto'],
                        total=json_data['total'],
                        costo_total=json_data['total'],
                        total_comision=json_data['total_comision'],
                        zona_id=cliente.zona_id if cliente.zona_id is not None else '',
                        nota=json_data['nota'],
                        sucursalid=sucursalid,
                        subtotal_iva=json_data['base_tarifa_iva'],
                        subtotal_cero=json_data['base_tarifa_cero'],
                        descuento_iva=json_data['base_descuento_iva'],
                        descuento_cero=json_data['base_descuento_cero'],
                        dias_credito=termino_dias,
                        vence=fecha_vence,
                        nocontrola_stock=json_data['controla_stock']
                    )
                    pedido.save()

                    for item in json_data['items']:
                        if item['cantidad'] > 0:
                            pedido_detalle = VenOrdenPedidosDetalle(
                                orden_pedido_id=pedido.id,
                                producto_id=item['productoid'],
                                bodega_id=pedido.bodega_id,
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
                                tasa_impuesto=item['tasaimpuesto'],
                                impuesto=item['impuesto'],
                                total=item['total'],
                                empaque=item['empaque'],
                                factor=item['factor'],
                                formato=item['formato'],
                                ctaimpuestoid=item['ctaimpuestoid'],
                                sucursalid=json_data['sucursalid'],
                                clase=item['clase'],
                                valor_comision=item['valor_comision'],
                                comision_contado=item['comision_contado'],
                                comision_credito=item['comision_credito'],
                                tasa_descuento_contado = item['tasa_descuento_contado'],
                                tasa_descuento_credito = item['tasa_descuento_credito'],
                                coniva=item['coniva']
                            )
                            pedido_detalle.save()

                            stock = 0
                            producto_stock = pedido_detalle.producto.get_bodega_stock(pedido.bodega_id,pedido.sucursalid)
                            if producto_stock is not None:
                                stock = producto_stock['stock']

                            if stock <= 0:
                                raise Exception("El producto {}:{} se encuentra SIN Stock en bodega: {}-{}".format(
                                    pedido_detalle.producto.codigo,
                                    pedido_detalle.producto.nombre_corto,
                                    pedido_detalle.bodega.codigo,
                                    pedido_detalle.bodega.nombre)
                                )
                            elif (Decimal(pedido_detalle.cantidad) * Decimal(pedido_detalle.factor)) > stock:
                                raise Exception("La cantidad del producto {}:{} supera el stock: {} : {}".format(pedido_detalle.producto.codigo,pedido_detalle.producto.nombre_corto,stock,pedido.bodega.nombre))

                            try:
                                pbodega = InvPdBodegaStock.objects.get(
                                    producto_id=item['productoid'],
                                    bodega_id=pedido.bodega_id,
                                    bodega__sucursal=pedido.sucursalid
                                )
                                pbodega.stock_reservado = round(pbodega.stock_reservado,2) + round(Decimal(item['cantidad']) * Decimal(item['factor']),2)
                                pbodega.save()
                            except:
                                raise Exception('Error en actualizar el Stock Reservado en bodega: {}'.format(pedido.bodega.nombre))

                    data['resp'] = True
                    return JsonResponse(data, status=200)

            #elif accion == 'orden_pedido_editar':

                # with transaction.atomic():
                #     json_data = json.loads(request.POST['pedido'])
                #     try:
                #         pedido = VenOrdenPedidos.objects.get(pk=json_data['pedidoid'])
                #     except:
                #         raise Exception("No se encontro la orden de pedido.")
                #
                #     if pedido.estado == '5'.strip():
                #         raise Exception("No se permite editar un pedido facturado.")
                #
                #     cliente = json_data['cliente']
                #     fecha = datetime.datetime.strptime(json_data['fecha'], '%d/%m/%Y')
                #
                #     pedido.cliente_id=json_data['clienteid']
                #     pedido.detalle=cliente['nombre']
                #     pedido.ruc=cliente['ruc']
                #     pedido.empleadoid=json_data['empleadoid']
                #     pedido.vendedor_id=cliente['vendedorid']
                #     pedido.caja_id=json_data['cajaid']
                #     pedido.terminoid=cliente['terminoid']
                #     pedido.division_id=json_data['divisionid']
                #     pedido.bodega_id=json_data['bodegaid']
                #     pedido.contado=json_data['contado']
                #     pedido.fecha=fecha
                #     pedido.entregado=fecha
                #     pedido.tipo=json_data['tipo']
                #     pedido.divisaid=json_data['divisaid']
                #     pedido.cambio=Decimal('1.00')
                #     pedido.subtotal=Decimal(json_data['subtotal'])
                #     pedido.descuento=Decimal(json_data['descuento'])
                #     pedido.impuesto=Decimal(json_data['impuesto'])
                #     pedido.total=Decimal(json_data['total'])
                #     pedido.costo_total=Decimal(json_data['total'])
                #     pedido.total_comision=Decimal(json_data['total_comision'])
                #     pedido.zona_id=cliente['zona_id']
                #     pedido.nota=json_data['nota']
                #     pedido.sucursalid=json_data['sucursalid']
                #     pedido.subtotal_cero=json_data['base_tarifa_cero']
                #     pedido.subtotal_iva=json_data['base_tarifa_iva']
                #     pedido.estado = '1'
                #     pedido.save()
                #
                #     productos_codigos = [e['codigo'] for e in json_data['items']]
                #
                #     for item in pedido.venordenpedidosdetalle_set.exclude(
                #             codigo__in=productos_codigos
                #         ):
                #         try:
                #             pbodega = InvPdBodegaStock.objects.get(
                #                 producto_id=item.producto_id,
                #                 bodega_id=pedido.bodega_id,
                #                 bodega__sucursal=pedido.sucursalid
                #             )
                #             pbodega.stock_reservado = round(pbodega.stock_reservado, 2) - round(Decimal(item.cantidad) * Decimal(item.factor), 2)
                #             pbodega.save()
                #         except:
                #             raise Exception('Error en actualizar el Stock Reservado en bodega: {}'.format(pedido.bodega.nombre))
                #
                #     pedido.venordenpedidosdetalle_set.exclude(codigo__in=productos_codigos).delete()
                #
                #     for item in json_data['items']:
                #         if Decimal(item['cantidad']) > 0:
                #
                #             pedido_detalles = VenOrdenPedidosDetalle.objects.filter(orden_pedido_id=pedido.id,codigo=item['codigo'],producto_id=item['productoid'])
                #             if pedido_detalles.exists():
                #
                #                 pedido_detalle = pedido_detalles[0]
                #                 cantidad_ant = round(pedido_detalle.cantidad,2)
                #
                #                 pedido_detalle.bodega_id = pedido.bodega_id
                #                 pedido_detalle.cantidad = round(item['cantidad'],2)
                #                 pedido_detalle.precio = item['precio']
                #                 pedido_detalle.precio_display = item['precio_display']
                #                 pedido_detalle.precio_factor = item['precio_factor']
                #                 pedido_detalle.precio_final = item['precio_final']
                #                 pedido_detalle.costo = item['costo_compra']
                #                 pedido_detalle.ctacosto_id = item['ctacosto_id']
                #                 pedido_detalle.ctadescuento_id = item['ctadescuento_id']
                #                 pedido_detalle.ctadevolucion_id = item['ctadevolucion_id']
                #                 pedido_detalle.ctaimpuestoid = item['ctaimpuestoid']
                #                 pedido_detalle.ctamayor_id = item['ctamayor_id']
                #                 pedido_detalle.ctaventa_id = item['ctaventa_id']
                #                 pedido_detalle.subtotal = item['subtotal']
                #                 pedido_detalle.tasa_descuento = item['tasadescuento']
                #                 pedido_detalle.descuento = item['descuento']
                #                 pedido_detalle.tasa_impuesto = item['tasaimpuesto']
                #                 pedido_detalle.impuesto = item['impuesto']
                #                 pedido_detalle.total = item['total']
                #                 pedido_detalle.empaque = item['empaque']
                #                 pedido_detalle.factor = item['factor']
                #                 pedido_detalle.sucursalid = json_data['sucursalid']
                #                 pedido_detalle.clase = item['clase']
                #                 pedido_detalle.valor_comision = item['valor_comision']
                #                 pedido_detalle.comision_contado = item['comision_contado']
                #                 pedido_detalle.comision_credito = item['comision_credito']
                #                 pedido_detalle.coniva = item['coniva']
                #                 pedido_detalle.save()
                #
                #                 if round(pedido_detalle.cantidad,2) != cantidad_ant:
                #                     try:
                #                         pbodega = InvPdBodegaStock.objects.get(
                #                             producto_id=item['productoid'],
                #                             bodega_id=pedido.bodega_id,
                #                             bodega__sucursal=pedido.sucursalid
                #                         )
                #                         if pedido_detalle.cantidad > cantidad_ant:
                #                             reservado = pedido_detalle.cantidad - cantidad_ant
                #
                #                             stock = 0
                #                             producto_stock = pedido_detalle.producto.get_bodega_stock(pedido.bodega_id,pedido.sucursalid)
                #                             if producto_stock is not None:
                #                                 stock = producto_stock['stock']
                #                             if stock <= 0:
                #                                 raise Exception(
                #                                     "El producto {}:{} se encuentra SIN Stock en bodega: {}-{}".format(
                #                                         pedido_detalle.producto.codigo,
                #                                         pedido_detalle.producto.nombre_corto,
                #                                         pedido_detalle.bodega.codigo,
                #                                         pedido_detalle.bodega.nombre)
                #                                 )
                #                             elif (reservado * pedido_detalle.factor) > stock:
                #                                 raise Exception("La cantidad del producto {}:{} supera el stock: {} : {}".format(
                #                                         pedido_detalle.producto.codigo,
                #                                         pedido_detalle.producto.nombre_corto, stock,
                #                                         pedido.bodega.nombre))
                #
                #                             pbodega.stock_reservado = round(pbodega.stock_reservado, 2) + round(Decimal(reservado) * Decimal(item['factor']), 2)
                #
                #                         else:
                #
                #                             reservado = cantidad_ant - pedido_detalle.cantidad
                #                             pbodega.stock_reservado = round(pbodega.stock_reservado, 2) - round(Decimal(reservado) * Decimal(item['factor']), 2)
                #
                #                         pbodega.save()
                #
                #                     except:
                #                         raise Exception('Error en actualizar el Stock Reservado en bodega: {}'.format(pedido.bodega.nombre))
                #
                #             else:
                #                 pedido_detalle = VenOrdenPedidosDetalle(
                #                     orden_pedido_id=pedido.id,
                #                     producto_id=item['productoid'],
                #                     bodega_id=pedido.bodega_id,
                #                     codigo=item['codigo'],
                #                     cantidad=item['cantidad'],
                #                     precio=item['precio'],
                #                     precio_display=item['precio_display'],
                #                     precio_factor=item['precio_factor'],
                #                     precio_final=item['precio_final'],
                #                     costo=item['costo_compra'],
                #                     ctacosto_id=item['ctacosto_id'],
                #                     ctadescuento_id=item['ctadescuento_id'],
                #                     ctadevolucion_id=item['ctadevolucion_id'],
                #                     ctaimpuestoid=item['ctaimpuestoid'],
                #                     ctamayor_id=item['ctamayor_id'],
                #                     ctaventa_id=item['ctaventa_id'],
                #                     subtotal=item['subtotal'],
                #                     tasa_descuento=item['tasadescuento'],
                #                     descuento=item['descuento'],
                #                     tasa_impuesto=item['tasaimpuesto'],
                #                     impuesto=item['impuesto'],
                #                     total=item['total'],
                #                     empaque=item['empaque'],
                #                     factor=item['factor'],
                #                     sucursalid=json_data['sucursalid'],
                #                     clase=item['clase'],
                #                     valor_comision=item['valor_comision'],
                #                     comision_contado=item['comision_contado'],
                #                     comision_credito=item['comision_credito'],
                #                     coniva=item['coniva']
                #                 )
                #                 pedido_detalle.save()
                #
                #                 stock = 0
                #                 producto_stock = pedido_detalle.producto.get_bodega_stock(pedido.bodega_id,pedido.sucursalid)
                #                 if producto_stock is not None:
                #                     stock = producto_stock['stock']
                #                 if stock <= 0:
                #                     raise Exception("El producto {}:{} se encuentra SIN Stock en bodega: {}-{}".format(
                #                         pedido_detalle.producto.codigo,
                #                         pedido_detalle.producto.nombre_corto,
                #                         pedido_detalle.bodega.codigo,
                #                         pedido_detalle.bodega.nombre)
                #                     )
                #                 elif (pedido_detalle.cantidad * pedido_detalle.factor) > stock:
                #                     raise Exception("La cantidad del producto {}:{} supera el stock: {} : {}".format(
                #                         pedido_detalle.producto.codigo,
                #                         pedido_detalle.producto.nombre_corto,
                #                         stock,
                #                         pedido.bodega.nombre)
                #                     )
                #                 try:
                #                     pbodega = InvPdBodegaStock.objects.get(
                #                         producto_id=item['productoid'],
                #                         bodega_id=pedido.bodega_id,
                #                         bodega__sucursal=pedido.sucursalid
                #                     )
                #                     pbodega.stock_reservado = round(pbodega.stock_reservado, 2) + round(Decimal(item['cantidad']) * Decimal(item['factor']), 2)
                #                     pbodega.save()
                #                 except:
                #                     raise Exception('Error en actualizar el Stock Reservado en bodega: {}'.format(pedido.bodega.nombre))
                #
                #     data['resp'] = True
                #     return JsonResponse(data, status=200)

        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, status=200)

    def get(self, request, *args, **kwargs):
        data = {
            "editar":False,
            "precio_lista": '1',
            "precio_activo": '2',
        }
        addUserData(request, data)
        try:
            pedido_id = kwargs.get("pk", None)
            hoy = data['hoy']

            if pedido_id is not None:
                data['accion'] = 'orden_pedido_editar'
                data['editar'] = True
                try:
                    pedido = VenOrdenPedidos.objects.get(pk=pedido_id)
                except:
                    raise Exception("No se encontro la orden de pedido.")

                if pedido.estado == '5'.strip():
                    raise Exception("No se permite editar un pedido facturado.")

                if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                    if pedido.creadopor.strip().upper() != request.user.username.strip().upper():
                        raise Exception("No se permite editar el pedido para el usuario actual..")

                data['pedido'] = pedido
                data['fecha'] = pedido.fecha
                data['fecha_entrega'] = pedido.entregado
                caja = pedido.caja
                if caja is None:
                    raise Exception('No se encontro caja asociado al usuario..')
                try:
                    data['cliente'] = pedido.cliente
                    data['empleado'] = request.user.segusuarioparametro.empleado
                except:
                    data['cliente'] = None
                    data['empleado'] = None

                data['caja_id'] = caja.id
                data['sucursal'] = pedido.sucursalid

                if caja.bodega is not None:
                    data['bodega'] = caja.bodega

            else:

                data['accion'] = 'orden_pedido_crear'
                data['fecha'] = hoy
                data['fecha_entrega'] = hoy

                caja = request.user.segusuarioparametro.caja
                if caja is None:
                    raise Exception('No se encontro caja asociado al usuario..')

                try:
                    data['cliente'] = cliente = CliClientes.objects.get(id='0000000001', anulado=False)
                    data['termino'] = SisParametros.objects.get(pk=cliente.termino)
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
            data['controla_stock'] = PEDIDOS_CONTROLA_STOCK

            if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                data['disabled'] = True

            return render(request, 'pedido/punto_orden_pedido.html', data)

        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')
