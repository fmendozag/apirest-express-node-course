import datetime
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Count, Max, F
from django.db.models.functions import Coalesce
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import ListView
from easy_pdf.rendering import render_to_pdf_response
from banco.models import BanBancos, BanIngresosDetalle
from cliente.models import CliClientesDeudas
from empleado.models import EmpEmpleados
from pedido.models import VenOrdenPedidos
from sistema.constantes import USER_ALL_PERMISOS, DIAS_SEMANA, NOMBRE_SISTEMA, LOGO_INFORME_CABECERA, \
    NOMBRE_INSTITUCION, INSTITUCION_CIUDAD, INSTITUCION_DIRECCION, INSTITUCION_DIRECCION2, INSTITUCION_TELEFONO
from sistema.funciones import addUserData
from sistema.models import SisDivisiones, SisZonas
from venta.models import VenFacturas, VenLiquidacionComision, VenLiquidacionMovimientos

class InformeFacturasView(LoginRequiredMixin,ListView):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    model = VenFacturas
    template_name = 'informe/ven_informe_factura.html'  # Default: <app_label>/<model_name>_list.html
    context_object_name = 'facturas'  # Default: object_list
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        addUserData(self.request, context)
        qs = kwargs.pop('facturas', self.object_list)
        context['total'] = 0.00
        total = qs.aggregate(total=Sum('total'))['total']
        if total is not None:
            context['total'] = total

        s = self.request.GET.get('s', '')
        divisionid = self.request.GET.get('divisionid', '')
        vendedorid = self.request.GET.get('vendedorid', '')
        usuarioid = self.request.GET.get('usuarioid', '')
        cajaid = self.request.GET.get('cajaid', '')

        inicio = self.request.GET.get('inicio', '')
        final = self.request.GET.get('final', '')

        url = '&s={}&inicio={}&final={}&divisionid={}&vendedorid={}&usuarioid={}&cajaid={}'.format(
          s,inicio, final,divisionid,vendedorid,usuarioid,cajaid
        )
        context['url'] = url
        context['s'] = s
        context['inicio'] = inicio
        context['final'] = final
        context['divisionid'] = divisionid
        context['vendedorid'] = vendedorid
        context['usuarioid'] = usuarioid
        context['cajaid'] = cajaid

        if not self.request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
            context['disabled'] = True

        context['divisiones'] = SisDivisiones.objects.all()
        context['usuarios'] = User.objects.filter(is_active=True)
        context['vendedores'] = EmpEmpleados.objects.filter(anulado=False,vendedor=True)
        context['cajas'] = BanBancos.objects.filter(anulado=False,clase='02')
        return context

    def get_queryset(self, **kwargs):
        search = self.request.GET.get('s', '')
        criterio = {
            'division_id': self.request.GET.get('divisionid', ''),
            'cliente__vendedor_id': self.request.GET.get('vendedorid', ''),
            'creadopor': self.request.GET.get('usuarioid', ''),
            'caja_id': self.request.GET.get('cajaid', ''),
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
            criterio['fecha__range'] = date_range
        except:
            pass

        def queries(filters):
            return [Q(**{k: v}) for k, v in filters.items() if v]

        return VenFacturas.objects.filter(
            Q(anulado=False),
            Q(numero__icontains=search) |
            Q(cliente__nombre__icontains=search),
            *queries(criterio)
        )

class InformePuntoVentaFacturasView(LoginRequiredMixin,ListView):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    model = VenFacturas
    template_name = 'informe/ven_informe_punto_venta_factura.html'  # Default: <app_label>/<model_name>_list.html
    context_object_name = 'facturas'  # Default: object_list
    paginate_by = 20
    es_cajero = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        addUserData(self.request, context)
        qs = kwargs.pop('facturas', self.object_list)
        context['total'] = qs.aggregate(total=Coalesce(Sum('total'),0))['total']

        s = self.request.GET.get('s', '')
        divisionid = self.request.GET.get('divisionid', '')
        vendedorid = self.request.GET.get('vendedorid', '')
        usuarioid = self.request.GET.get('usuarioid', '')
        cajaid = self.request.GET.get('cajaid', '')

        inicio = self.request.GET.get('inicio', '')
        final = self.request.GET.get('final', '')

        url = '&s={}&inicio={}&final={}&divisionid={}&vendedorid={}&usuarioid={}&cajaid={}'.format(
          s,inicio, final,divisionid,vendedorid,usuarioid,cajaid
        )
        context['url'] = url
        context['s'] = s
        context['inicio'] = inicio
        context['final'] = final
        context['divisionid'] = divisionid
        context['vendedorid'] = vendedorid
        context['usuarioid'] = usuarioid
        context['cajaid'] = cajaid

        if self.es_cajero:
            caja = self.request.user.segusuarioparametro.caja
            context['divisiones'] = SisDivisiones.objects.filter(pk=caja.division_id)
            context['usuarios'] = User.objects.filter(is_active=True,username=self.request.user.username)
            context['cajas'] = BanBancos.objects.filter(anulado=False,clase='02',pk=caja.id)
        else:
            context['divisiones'] = SisDivisiones.objects.all()
            context['usuarios'] = User.objects.filter(is_active=True)
            context['vendedores'] = EmpEmpleados.objects.filter(anulado=False, vendedor=True)
            context['cajas'] = BanBancos.objects.filter(anulado=False, clase='02')

        return context

    def get_queryset(self, **kwargs):
        search = self.request.GET.get('s', '')
        if self.request.session['grupoid'] in (5,):
            caja = self.request.user.segusuarioparametro.caja
            criterio = {
                'creadopor': self.request.user.username,
                'caja_id': caja.id
            }
            self.es_cajero = True
        else:
            criterio = {
                'division_id': self.request.GET.get('divisionid', ''),
                'cliente__vendedor_id': self.request.GET.get('vendedorid', ''),
                'creadopor': self.request.GET.get('usuarioid', ''),
                'caja_id': self.request.GET.get('cajaid', ''),
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

        return VenFacturas.objects.filter(
            Q(anulado=False),
            Q(numero__icontains=search) |
            Q(ruc__icontains=search) |
            Q(cliente__nombre__icontains=search),
            *queries(criterio)
        )

class InformeFacturasCartillasView(LoginRequiredMixin,ListView):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    model = VenFacturas
    template_name = 'informe/ven_informe_factura_cartilla.html'  # Default: <app_label>/<model_name>_list.html
    context_object_name = 'facturas'  # Default: object_list
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        addUserData(self.request, context)
        qs = kwargs.pop('facturas', self.object_list)
        context['total'] = 0.00
        total = qs.aggregate(total=Sum('total'))['total']
        if total is not None:
            context['total'] = total

        s = self.request.GET.get('s', '')
        divisionid = self.request.GET.get('divisionid', '')
        vendedorid = self.request.GET.get('vendedorid', '')
        usuarioid = self.request.GET.get('usuarioid', '')
        cajaid = self.request.GET.get('cajaid', '')

        inicio = self.request.GET.get('inicio', '')
        final = self.request.GET.get('final', '')

        url = '&s={}&inicio={}&final={}&divisionid={}&vendedorid={}&usuarioid={}&cajaid={}'.format(
          s,inicio, final,divisionid,vendedorid,usuarioid,cajaid
        )
        context['url'] = url
        context['s'] = s
        context['inicio'] = inicio
        context['final'] = final
        context['divisionid'] = divisionid
        context['vendedorid'] = vendedorid
        context['usuarioid'] = usuarioid
        context['cajaid'] = cajaid

        if not self.request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
            context['disabled'] = True

        context['divisiones'] = SisDivisiones.objects.all()
        context['usuarios'] = User.objects.filter(is_active=True)
        context['vendedores'] = EmpEmpleados.objects.filter(anulado=False,vendedor=True)
        context['cajas'] = BanBancos.objects.filter(anulado=False,clase='02')
        return context

    def get_queryset(self, **kwargs):
        search = self.request.GET.get('s', '')
        criterio = {
            'division_id': self.request.GET.get('divisionid', ''),
            'vendedorid': self.request.GET.get('vendedorid', ''),
            'creadopor': self.request.GET.get('usuarioid', ''),
            'caja_id': self.request.GET.get('cajaid', ''),
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
            criterio['fecha__range'] = date_range
        except:
            pass

        def queries(filters):
            return [Q(**{k: v}) for k, v in filters.items() if v]

        return VenFacturas.objects.filter(
            Q(anulado=False),
            Q(numcartilla__isnull=False),
            Q(numero__icontains=search) |
            Q(cliente__nombre__icontains=search),
            *queries(criterio)
        ).exclude(numcartilla__exact='').order_by(
           'numcartilla','-fecha'
        )

class InformeComisionLiquidacionView(LoginRequiredMixin,ListView):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    model = VenFacturas
    template_name = 'informe/informe_comision_liquidacion.html'  # Default: <app_label>/<model_name>_list.html
    context_object_name = 'comisiones'  # Default: object_list
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        addUserData(self.request, context)
        qs = kwargs.pop('facturas', self.object_list)
        context['total'] = 0.00
        total = qs.aggregate(total=Sum('total'))['total']
        if total is not None:
            context['total'] = total

        s = self.request.GET.get('s', '')
        divisionid = self.request.GET.get('divisionid', '')
        usuarioid = self.request.GET.get('usuarioid', '')
        vendedorid = self.request.GET.get('vendedorid', '')

        inicio = self.request.GET.get('inicio', '')
        final = self.request.GET.get('final', '')

        url = '&s={}&inicio={}&final={}&divisionid={}&vendedorid={}&usuarioid={}'.format(
          s,inicio, final,divisionid,vendedorid,usuarioid
        )
        context['url'] = url
        context['s'] = s
        context['inicio'] = inicio
        context['final'] = final
        context['divisionid'] = divisionid
        context['usuarioid'] = usuarioid
        context['vendedorid'] = vendedorid

        if not self.request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
            context['disabled'] = True
        context['divisiones'] = SisDivisiones.objects.all()
        context['usuarios'] = User.objects.filter(is_active=True)
        context['vendedores'] = EmpEmpleados.objects.filter(anulado=False,vendedor=True)
        return context

    def get_queryset(self, **kwargs):
        search = self.request.GET.get('s', '')
        criterio = {
            'division_id': self.request.GET.get('divisionid', ''),
            'creadopor': self.request.GET.get('usuarioid', ''),
            'vendedor_id': self.request.GET.get('vendedorid', ''),
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
            criterio['fecha__range'] = date_range
        except:
            pass

        def queries(filters):
            return [Q(**{k: v}) for k, v in filters.items() if v]

        return VenLiquidacionComision.objects.filter(
            Q(anulado=False),
            Q(numero__icontains=search) |
            Q(vendedor__cedula__icontains=search) |
            Q(vendedor__nombre__icontains=search),
            *queries(criterio)
        )

class InformeArqueoCajaView(LoginRequiredMixin,ListView):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'
    model = BanIngresosDetalle
    template_name = 'informe/ban_informe_arqueo_caja.html'  # Default: <app_label>/<model_name>_list.html
    context_object_name = 'pagos'  # Default: object_list
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        addUserData(self.request, context)
        qs = kwargs.pop('pagos', self.object_list)
        context['total'] = 0.00

        total = qs.aggregate(total=Coalesce(Sum('valor'),0))['total']
        if total is not None:
            context['total'] = total

        s = self.request.GET.get('s', '')
        bancoid = self.request.GET.get('bancoid', '')
        divisionid = self.request.GET.get('divisionid', '')
        usuarioid = self.request.GET.get('usuarioid', '')

        inicio = self.request.GET.get('inicio', '')
        final = self.request.GET.get('final', '')

        url = '&s={}&inicio={}&final={}&divisionid={}&usuarioid={}&bancoid={}'.format(
          s,inicio,final,divisionid,usuarioid,bancoid
        )
        context['url'] = url
        context['s'] = s
        context['inicio'] = inicio
        context['final'] = final
        context['divisionid'] = divisionid
        context['usuarioid'] = usuarioid
        context['bancoid'] = bancoid

        if not self.request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
            context['disabled'] = True

        context['divisiones'] = SisDivisiones.objects.all()
        context['usuarios'] = User.objects.filter(is_active=True)
        context['bancos'] = BanBancos.objects.filter(anulado=False)
        return context

    def get_queryset(self, **kwargs):
        search = self.request.GET.get('s', '')
        criterio = {
            'ingreso__banco_id': self.request.GET.get('bancoid', ''),
            'ingreso__divisionid': self.request.GET.get('divisionid', ''),
            'creadopor': self.request.GET.get('usuarioid', ''),
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
            criterio['fecha__range'] = date_range
        except:
            pass

        def queries(filters):
            return [Q(**{k: v}) for k, v in filters.items() if v]

        return BanIngresosDetalle.objects.values(
            'id','fecha','tipo','valor','creadopor','creadodate',
            documento=F('ingreso__numero'),
            cartilla=F('numcartilla'),
            detalle=F('ingreso__detalle'),
            recibo=F('recibopago'),
            zona=F('ingreso__deudor__zona__nombre'),
        ).filter(
            Q(ingreso__anulado=False),
            Q(tipo='EFECTIVO'),
            Q(ingreso__numero__icontains=search) |
            Q(numcartilla__icontains=search),
            *queries(criterio)
        ).annotate(
            item=Count('id'),
        ).order_by('-fecha','creadopor')

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def informe_vendedor_comisiones(request,tipo,pk):
    if request.method == 'GET':
        data = {}
        try:
            comision = VenLiquidacionComision.objects.get(pk=pk)
            pendientes = VenLiquidacionMovimientos.objects.filter(
                anulado=False,
                fecha__date__lte=comision.fecha,
                vendedor_id=comision.vendedor.id,
                saldo__gt=0,
                credito=False
            ).exclude(
                documentoid__in=[
                    e[0] for e in comision.venliquidacioncomisiondetalle_set.values_list('factura_id').filter(anulado=False)
                ]
            ).order_by('fecha', 'cliente__nombre')

            lista_pendientes = []
            for p in pendientes:
                pagos = CliClientesDeudas.objects.filter(
                    anulado=False,
                    numcartilla=p.numcartilla,
                    cliente_id=p.cliente_id,
                    credito=True,
                    fecha__date__lte=comision.fecha.date()
                ).aggregate(haber=Coalesce(Sum('valor'), 0), cantidad=Count('valor'))

                lista_pendientes.append({
                    "numcartilla": p.numcartilla,
                    "cliente":p.cliente.nombre,
                    "telefono":p.cliente.telefono1,
                    "fecha": p.fecha,
                    "dias": (comision.fecha.date() - p.fecha.date()).days,
                    "contado": p.contado,
                    "valor_credito": p.valor_credito,
                    "valor_abonos": round(Decimal(pagos['haber']), 2),
                    "abonos": int(pagos['cantidad']),
                    "saldo": p.saldo
                })

            data['total_pendiente'] = pendientes.aggregate(total=Coalesce(Sum('saldo'), 0))['total']
            data['comision'] = comision
            data['pendientes'] = lista_pendientes

            if tipo == 'pdf':
                return render_to_pdf_response(request,"informe/ven_informe_vendedor_comision.html", data)
        except:
            raise
    return redirect('/')

class InformeCatalogoView(LoginRequiredMixin,ListView):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    model = VenFacturas
    template_name = 'informe/ven_informe_catalogo_cliente.html'  # Default: <app_label>/<model_name>_list.html
    context_object_name = 'clientes'  # Default: object_list
    paginate_by = 16

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        addUserData(self.request, context)
        s = self.request.GET.get('s', '')
        divisionid = self.request.GET.get('divisionid', '')
        vendedorid = self.request.GET.get('vendedorid', '')
        usuarioid = self.request.GET.get('usuarioid', '')
        tipo_caja = self.request.GET.get('tipo_caja', '')
        sectorid = self.request.GET.get('sectorid', '')
        ciudadid = self.request.GET.get('ciudadid', '')
        zonaid = self.request.GET.get('zonaid', '')

        inicio = self.request.GET.get('inicio', '')
        final = self.request.GET.get('final', '')

        url = '&s={}&inicio={}&final={}&divisionid={}&vendedorid={}&usuarioid={}&tipo_caja={}&sectorid={}&ciudadid={}&zonaid={}'.format(
          s,inicio, final,divisionid,vendedorid,usuarioid,tipo_caja,sectorid,ciudadid,zonaid
        )
        context['url'] = url
        context['s'] = s
        context['inicio'] = inicio
        context['final'] = final
        context['divisionid'] = divisionid
        context['vendedorid'] = vendedorid
        context['usuarioid'] = usuarioid
        context['tipo_caja'] = tipo_caja
        context['sectorid'] = sectorid
        context['ciudadid'] = ciudadid
        context['zonaid'] = zonaid

        if not self.request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
            context['disabled'] = True

        context['divisiones'] = SisDivisiones.objects.all()
        context['usuarios'] = User.objects.filter(is_active=True)
        context['dias_semana'] = DIAS_SEMANA
        context['ciudades'] = SisZonas.objects.filter(anulado=False,tipo='CIUDAD').order_by('nombre')

        if ciudadid:
            context['sectores'] = SisZonas.objects.filter(anulado=False, tipo='OTRO',padre_id=ciudadid).order_by('codigo')
            context['zonas'] = SisZonas.objects.filter(anulado=False,tipo='ZONAS',padre__padre_id=ciudadid).order_by('nombre')
        else:
            context['zonas'] = SisZonas.objects.filter(anulado=False, tipo='ZONAS').order_by('nombre')
            context['sectores'] = SisZonas.objects.filter(anulado=False, tipo='OTRO').order_by('codigo')

        context['vendedores'] = EmpEmpleados.objects.filter(anulado=False,vendedor=True)
        return context

    def get_queryset(self, **kwargs):
        search = self.request.GET.get('s', '')
        criterio = {
            'cliente__zona_id': self.request.GET.get('zonaid', ''),
            'cliente__zona__padre_id': self.request.GET.get('sectorid', ''),
            'cliente__zona__padre__padre_id': self.request.GET.get('ciudadid', ''),
            'cliente__vendedor_id': self.request.GET.get('vendedorid', ''),
            'creadopor': self.request.GET.get('usuarioid', ''),
            'caja__cobertura': self.request.GET.get('tipo_caja', ''),
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
            criterio['fecha__range'] = date_range
        except:
            pass

        def queries(filters):
            return [Q(**{k: v}) for k, v in filters.items() if v]

        return VenFacturas.objects.values(
            'cliente_id',ruc_ced=F('cliente__ruc'),nombre=F('cliente__nombre')
        ).filter(
            Q(anulado=False),
            Q(cliente__ruc__icontains=search) |
            Q(cliente__nombre__icontains=search),
            *queries(criterio)
        ).annotate(
            valor=Max('total'),
            fecha=Max('fecha'),
            telefono=F('cliente__telefono1'),
            direccion=F('cliente__direccion'),
            zona=F('cliente__zona__nombre'),
            sector=F('cliente__zona__padre__codigo'),
            visita=F('cliente__dia_visita')
        ).order_by(
           'sector','zona'
        )

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def orden_pedido_documento(request,tipo,pid,name):
    if request.method == 'GET':
        data = {}
        try:
            try:
                pedido = VenOrdenPedidos.objects.get(pk=pid,anulado=False)
            except:
                raise Http404("Fallido!, No se encontró registro orden de pedido")

            data['title'] = 'Documento orden de pedido'
            data['sistema'] = NOMBRE_SISTEMA
            data['logo_cabecera'] = LOGO_INFORME_CABECERA
            data['belbry'] = NOMBRE_INSTITUCION
            data['ciudad'] = INSTITUCION_CIUDAD
            data['direccion'] = INSTITUCION_DIRECCION
            data['direccion2'] = INSTITUCION_DIRECCION2
            data['telefono'] = INSTITUCION_TELEFONO
            data['hoy'] = datetime.datetime.now()
            data['pedido'] = pedido
            data['usuario'] = request.user.username
            data['titulo'] = 'documento_pedido'
            if tipo == 'pdf':
                return render_to_pdf_response(request,"informe/pedidos/ped_informe_pedido_pdf.html", data)
        except:
            raise
    return redirect('/')

class InformeLiquidacionVentasView(LoginRequiredMixin,ListView):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    model = VenFacturas
    template_name = 'informe/ven_informe_liquidacion_ventas.html'  # Default: <app_label>/<model_name>_list.html
    context_object_name = 'facturas'  # Default: object_list
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        addUserData(self.request, context)
        qs = kwargs.pop('facturas', self.object_list)
        context['total'] = 0.00
        total = qs.aggregate(total=Sum('total'))['total']
        if total is not None:
            context['total'] = total

        s = self.request.GET.get('s', '')
        divisionid = self.request.GET.get('divisionid', '')
        vendedorid = self.request.GET.get('vendedorid', '')
        usuarioid = self.request.GET.get('usuarioid', '')

        inicio = self.request.GET.get('inicio', '')
        final = self.request.GET.get('final', '')

        url = '&s={}&inicio={}&final={}&divisionid={}&vendedorid={}&usuarioid={}'.format(
          s,inicio, final,divisionid,vendedorid,usuarioid
        )
        context['url'] = url
        context['s'] = s
        context['inicio'] = inicio
        context['final'] = final
        context['divisionid'] = divisionid
        context['vendedorid'] = vendedorid
        context['usuarioid'] = usuarioid

        if not self.request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
            context['disabled'] = True

        context['divisiones'] = SisDivisiones.objects.all()
        context['usuarios'] = User.objects.filter(is_active=True)
        context['vendedores'] = EmpEmpleados.objects.filter(anulado=False,vendedor=True)
        return context

    def get_queryset(self, **kwargs):
        search = self.request.GET.get('s', '')
        criterio = {
            'division_id': self.request.GET.get('divisionid', ''),
            'vendedorid': self.request.GET.get('vendedorid', ''),
            'creadopor': self.request.GET.get('usuarioid', '')
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
            criterio['fecha__range'] = date_range
        except:
            pass

        def queries(filters):
            return [Q(**{k: v}) for k, v in filters.items() if v]

        lista_ventas = []
        # for v in VenFacturas.objects.filter(
        #     Q(anulado=False),
        #     Q(caja__ctamayorid='0000000676'),
        #     Q(numero__icontains=search) |
        #     Q(numcartilla__icontains=search) |
        #     Q(cliente__ruc__icontains=search) |
        #     Q(cliente__nombre__icontains=search),
        #     *queries(criterio)):
        #
        #     pagos = CliClientesDeudas.objects.filter(
        #         anulado=False,
        #         documentoid=v.id,
        #         cliente_id=v.cliente_id,
        #         credito=True,
        #         fecha__date__lte=v.fecha.date(),
        #         tipo__in=['VEN-FA','VEN-NV','']
        #     ).aggregate(haber=Coalesce(Sum('valor'), 0), cantidad=Count('valor'))
        #
        #     lista_ventas.append({
        #         "venta":v,
        #
        #     })
        return lista_ventas
