import datetime
import json
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.views.generic import ListView
from django.views.generic.base import View
from empleado.models import EmpEmpleados
from inventario.models import InvPdBodegaStock
from pedido.models import VenOrdenPedidos, VenOrdenPedidosDetalle
from sistema.constantes import ESTADO_ORDEN_PEDIDO, USER_ALL_PERMISOS
from sistema.funciones import addUserData
from sistema.models import SisDivisiones

COLOR = ('', 'warning', 'primary', 'danger','secondary','success')

class InformeChequearPedidosView(LoginRequiredMixin, ListView):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    model = VenOrdenPedidos
    template_name = 'pedido/ped_chequear_orden_pedido.html'  # Default: <app_label>/<model_name>_list.html
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
            Q(cliente__ruc__icontains=search) |
            Q(cliente__nombre__icontains=search),
            *queries(criterio)
        )

class OrdenPedidoChequearDetalle(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        try:
            accion = request.POST.get('accion')
            if accion == 'orden_pedido':
                pedido_id = request.POST.get('pedido_id')
                try:
                    pedido = VenOrdenPedidos.objects.get(pk=pedido_id)
                except:
                    raise Exception('No se encontro orden de pedido')

                lista_detalle = []
                for item in pedido.venordenpedidosdetalle_set.all():
                    lista_detalle.append({
                        'id': item.id,
                        'pedido_id': pedido.id,
                        'productoid': item.producto_id,
                        'producto_nombre': item.producto.nombre,
                        'codigo': item.codigo,
                        'coniva': item.coniva,
                        'cantidad': item.cantidad,
                        'empaque': item.empaque,
                        'precio': item.precio,
                        'factor': item.factor,
                        'precio_factor': item.precio_factor,
                        'precio_final': item.precio_final,
                        'precio_display': item.precio_display,
                        'total': round(item.total, 2),
                        'aprobado': item.aprobado,
                        'sugerido': round(item.sugerido,2),
                    })

                data['pedido'] = {
                    'id': pedido.id,
                    'numero': pedido.numero,
                    'fecha': pedido.fecha.date(),
                    'cliente_id': pedido.cliente_id,
                    'cliente_nombre': pedido.cliente.nombre,
                    'vendedor_nombre': pedido.vendedor.nombre,
                    'subtotal': pedido.subtotal,
                    'impuesto': pedido.impuesto,
                    'total': pedido.total,
                    'items': lista_detalle,
                    'estado': pedido.estado,
                    'estado_nombre': pedido.get_estado_display(),
                    'color': COLOR[int(pedido.estado)],
                    'observacion': pedido.aprobadonota
                }
                data['resp'] = True
                return JsonResponse(data, status=200)

            elif accion == 'update-pedido-detalle-aprobado':

                pedido_id = request.POST.get('pedido_id')
                id = request.POST.get('id')
                try:
                    pedido_detalle = VenOrdenPedidosDetalle.objects.get(pk=id, orden_pedido_id=pedido_id)
                except:
                    raise Exception('No se encontro orden de pedido detalle')

                if pedido_detalle.orden_pedido.estado == '5':
                    raise Exception("No se permite editar un pedido Facturado.")

                pedido_detalle.aprobado = request.POST.get('estado', '0')
                pedido_detalle.save()
                data['resp'] = True
                return JsonResponse(data, status=200)

            elif accion == 'orden-pedido-update-estado':
                pedido_id = request.POST.get('pedido_id')
                estado = request.POST.get('estado')
                aprobado = request.POST.get('aprobado')
                observacion = request.POST.get('observacion')

                try:
                    pedido = VenOrdenPedidos.objects.get(pk=pedido_id)
                except:
                    raise Exception('No se encontro orden de pedido')

                if pedido.estado == '5':
                    raise Exception("No se permite editar un pedido Facturado.")

                pedido.estado = estado
                pedido.aprobado = aprobado
                pedido.aprobadonota = observacion
                pedido.aprobadodate = datetime.datetime.now()
                pedido.aprobadopor = request.user.username
                pedido.save()

                json_items = json.loads(request.POST['items'])
                for item in json_items:
                    try:
                        if Decimal(item['sugerido']) > 0:
                            pedido_id = item['pedido_id']
                            id = item['id']
                            pedido_detalle = VenOrdenPedidosDetalle.objects.get(pk=id, orden_pedido_id=pedido_id)
                            pedido_detalle.sugerido = Decimal(item['sugerido'])
                            pedido_detalle.save()
                    except:
                        pass
                data['pedido'] = {
                    "id": pedido.id,
                    'estado': pedido.estado,
                    'estado_nombre': pedido.get_estado_display(),
                    'color': COLOR[int(pedido.estado)]
                }
                data['resp'] = True
                return JsonResponse(data, status=200)

            elif accion == 'update-pedido-anular':
                pedido_id = request.POST.get('pedido_id')
                estado = request.POST.get('estado')
                motivo = request.POST.get('motivo','')
                try:
                    pedido = VenOrdenPedidos.objects.get(pk=pedido_id)
                except:
                    raise Exception('No se encontro orden de pedido')

                if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                    if pedido.creadopor.strip().upper() != request.user.username.strip().upper():
                        raise Exception("No se permite anular el pedido para el usuario actual..")

                if not pedido.estado in '5':
                    pedido.estado = estado
                    pedido.anuladonota =motivo
                    pedido.anuladodate = datetime.datetime.now()
                    pedido.anuladopor = request.user.username
                    pedido.save()

                    for item in pedido.venordenpedidosdetalle_set.all():
                        try:
                            pbodega = InvPdBodegaStock.objects.get(
                                producto_id=item.producto_id,
                                bodega_id=item.bodega_id,
                                bodega__sucursal=item.sucursalid
                            )
                            if pedido.estado == '3':
                                pbodega.stock_reservado = round(pbodega.stock_reservado, 2) - round(Decimal(item.cantidad) * Decimal(item.factor), 2)
                            else:
                                pbodega.stock_reservado = round(pbodega.stock_reservado, 2) + round(Decimal(item.cantidad) * Decimal(item.factor), 2)

                            if pbodega.stock_reservado < 0:
                                raise

                            pbodega.save()
                        except:
                            raise Exception('Error en actualizar el Stock Reservado en bodega: {}'.format(item.bodega.nombre))

                    data['resp'] = True
                    return JsonResponse(data, status=200)
                else:
                    raise Exception('No se puede anular la orden de pedido')

            elif accion == 'update-pedido-detalle-aprobado-all':
                pedido_id = request.POST.get('pedidoid')
                try:
                    pedido = VenOrdenPedidos.objects.get(pk=pedido_id)
                except:
                    raise Exception('No se encontro orden de pedido')

                if pedido.estado == '5':
                    raise Exception("No se permite editar un pedido Facturado.")

                json_items = json.loads(request.POST['items'])
                for item in json_items:
                    pedido_id = item['pedido_id']
                    id = item['id']
                    try:
                        pedido_detalle = VenOrdenPedidosDetalle.objects.get(pk=id, orden_pedido_id=pedido_id)
                        pedido_detalle.aprobado = item['estado']
                        pedido_detalle.save()
                    except:
                        pass
                data['resp'] = True
                return JsonResponse(data, status=200)

        except Exception as e:
            data['error'] = 'error: ' + str(e)
        return JsonResponse(data, status=200)
