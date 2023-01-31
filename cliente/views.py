import datetime
import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction, connection
from django.db.models import Q, Sum
from django.http import JsonResponse, Http404
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.views.generic.base import View

from banco.models import BanBancos, BanIngresos, BanIngresosDetalle, BanIngresosDeudas
from cliente.forms import CliClientesForm
from cliente.models import CliClientes, CliClientesDeudas
from contabilidad.models import AccAsientos
from contadores.fn_contador import get_contador_sucdiv
from empleado.models import EmpEmpleados
from sistema.constantes import USER_ALL_PERMISOS, DIAS_SEMANA
from sistema.funciones import addUserData
from sistema.models import SisSucursales, SisZonas, SisDivisiones, SisParametros
from venta.models import VenFacturas

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def get_consulta_cliente(request):
    data = {'resp': False, 'error': ''}
    if request.method == 'POST':
        try:
            accion = request.POST.get('accion')
            if accion == 'cliente_ruc':
                c = CliClientes.objects.filter(ruc=request.POST.get('cliente_ruc'), anulado=False).first()
                data['cliente'] = {
                    "id": c.id,
                    "cod": c.codigo,
                    "ruc": c.ruc,
                    "nombre": c.nombre,
                    "codgrupo": c.grupo.codigo,
                    "folder": c.folder if c.folder is not None else '',
                    "direc": c.direccion,
                    "telef": c.telefono1 if c.telefono1 is not None else '',
                    "cupo": c.cupo,
                    "formapago": c.forma_pago,
                    "terminoid": c.termino if c.termino is not None else '',
                    "zona_id": c.zona_id,
                    "cupo": c.cupo,
                    "vendedorid": c.vendedor_id if c.vendedor_id is not None else '',
                    "vendedor": c.vendedor.nombre if c.vendedor_id is not None else ''
                }
                data['resp'] = True
                return JsonResponse(data, status=200)

            if accion == 'detalle_deuda_cartilla':
                num_carrilla = request.POST.get('numcartilla', None)
                if VenFacturas.objects.filter(anulado=False, numcartilla=num_carrilla).exists():
                    factura = VenFacturas.objects.get(
                        anulado=False,
                        numcartilla=num_carrilla
                    )

                    if factura.vendedorid is not None:
                        try:
                            vendedor = EmpEmpleados.objects.get(id=factura.vendedorid)
                        except:
                            vendedor = None

                    if factura.recaudadorid is not None:
                        try:
                            recaudador = EmpEmpleados.objects.get(id=factura.recaudadorid)
                        except:
                            recaudador = None

                    if factura.entregadorid is not None:
                        try:
                            entregador = EmpEmpleados.objects.get(id=factura.entregadorid)
                        except:
                            entregador = None

                    data['cliente'] = {
                        "documentoid": factura.id,
                        "clienteid": factura.cliente.id,
                        "cod": factura.cliente.codigo,
                        "ruc": factura.cliente.ruc,
                        "nombre": factura.cliente.nombre,
                        "dia": factura.dia_cobro,
                        "pago": factura.pagada,
                        "divisionid": factura.division.id,
                        "division": factura.division.nombre,
                        "bodega": factura.bodega.id,
                        "tipo": factura.tipo,
                        "total": factura.total,
                        "vendid": vendedor.id if vendedor is not None else '',
                        "vendcod": vendedor.codigo if vendedor is not None else '',
                        "vend": vendedor.nombre if vendedor is not None else '',
                        "recaudador": recaudador.nombre if recaudador is not None else '',
                        "entregador": entregador.nombre if entregador is not None else '',
                        "zonaid": factura.zona.id if factura.zona is not None else '',
                        "zona": factura.zona.nombre if factura.zona is not None else '',
                        "numcartilla": factura.numcartilla
                    }

                    lista_deudas = []
                    for d in CliClientesDeudas.objects.filter(anulado=False, cliente_id=factura.cliente.id,
                                                              numcartilla=factura.numcartilla, saldo__gt=0):
                        lista_deudas.append({
                            "deudaid": d.id,
                            "clienteid": d.cliente.id,
                            "numero": d.numero,
                            "fecha": d.fecha.date(),
                            "detalle": d.detalle,
                            "saldo": d.saldo,
                            "nuevosaldo": d.saldo,
                            "vencimiento": d.vencimiento.date(),
                            "tipo": d.tipo,
                            "ctacxid": d.cta_cxcobrar.id,
                            "rubroid": d.rubro.id,
                            "docid": d.documentoid,
                            "cambio": d.cambio,
                            "valor": d.valor,
                            "codrubro": d.rubro.codigo,
                            "rubro": d.rubro.nombre,
                            "credito": d.credito,
                            "divisionid": d.divisionid,
                            "divisaid": d.divisaid,
                            "numcartilla": d.numcartilla,
                        })

                    data['deuda'] = lista_deudas
                    data['resp'] = True
                else:
                    raise Exception('Numero de cartilla no existe.')
                return JsonResponse(data, status=200)

        except Exception as e:
            data['error'] = 'error: ' + str(e)
    else:
        try:
            accion = request.GET.get('accion')
            if accion == 'cliente_buscar':
                s = '%{}%'.format(request.GET.get('criterio', ''))
                personas = CliClientes.objects.extra(
                    where=["UPPER([CLI_CLIENTES].[Nombre]) LIKE UPPER(%s)"], params=[s]
                ).exclude(pk='0000000001').filter(
                    anulado=False
                ).order_by('nombre')[:25]
                lista_personas = []
                for p in personas:
                    try:
                        termino = SisParametros.objects.get(pk=p.termino)
                    except:
                        termino = None

                    lista_personas.append({
                        "id": p.id,
                        "cod": p.codigo.strip(),
                        "ruc": p.ruc.strip(),
                        "nombre": '{} : {}'.format(p.nombre,p.ruc.strip()),
                        "precio_lista": p.precio_lista,
                        "precio_activo": p.precio_activo,
                        "lista_precio": p.get_precio_activo_display(),
                        "terminoid": p.termino,
                        "termino_display": termino.nombre if termino is not None else '',
                        "termino_cod": termino.codigo if termino is not None else '',
                        "zona_id": p.zona_id,
                        "cupo": p.cupo,
                        "vendedorid": p.vendedor_id if p.vendedor_id is not None else '',
                        "vendedor": p.vendedor.nombre if p.vendedor_id is not None else '',
                        "tasa_descuento": round(p.tasa_descuento, 2),
                        "tasa_incremento": round(p.tasa_incremento, 2)
                    })
                return JsonResponse({"items": lista_personas}, status=200)

            elif accion == 'cliente-ruc':
                try:
                    p = CliClientes.objects.filter(ruc=request.GET.get('ruc'), anulado=False).first()
                except:
                    raise Exception('No se encontro cliente con el numero ingresado..')

                try:
                    termino = SisParametros.objects.get(pk=p.termino)
                except:
                    termino = None

                saldo = Decimal('0.00')
                disponible = Decimal('0.00')

                try:
                    if p.empleadoid is not None and p.empleadoid.strip() != '':
                        empleado = EmpEmpleados.objects.get(pk=p.empleadoid)
                        saldo = p.get_saldo_total() + empleado.get_saldo_total_empleado()
                    else:
                        saldo = p.get_saldo_total()
                    disponible = p.cupo - saldo
                except:
                    pass

                data['cliente'] = {
                    "id": p.id,
                    "cod": p.codigo.strip(),
                    "ruc": p.ruc.strip(),
                    "nombre": p.nombre,
                    "precio_lista": p.precio_lista,
                    "precio_activo": p.precio_activo,
                    "lista_precio": p.get_precio_activo_display(),
                    "terminoid": p.termino,
                    "termino_display": termino.nombre if termino is not None else '',
                    "termino_cod": termino.codigo if termino is not None else '',
                    "zona_id": p.zona_id,
                    "cupo": round(p.cupo,2),
                    "saldo": round(saldo,2),
                    "disponible": round(disponible,2),
                    "vendedorid": p.vendedor_id if p.vendedor_id is not None else '',
                    "vendedor": p.vendedor.nombre if p.vendedor_id is not None else '',
                    "tasa_descuento": round(p.tasa_descuento, 2),
                    "tasa_incremento": round(p.tasa_incremento, 2)
                }
                data['resp'] = True
                return JsonResponse(data, status=200)
        except Exception as e:
            data['error'] = str(e)
    return JsonResponse(data, status=200)

class CliDocumentoIngresoPago(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        accion = request.POST['accion']
        try:
            if accion == 'ingreso_dinero':

                with transaction.atomic():

                    json_data = json.loads(request.POST['factura'])
                    sucursalid = json_data['sucursalid']
                    divisionid = json_data['divisionid']
                    divisaid = json_data['divisaid']

                    banco_ingresoid = get_contador_sucdiv('BAN_INGRESOS-ID-', '{}{}'.format(sucursalid, divisionid[-1]))
                    banco_ingreso_numero = get_contador_sucdiv('BAN_INGRESOS-NUMBER-',
                                                               '{}{}'.format(sucursalid, divisionid[-1]))
                    asientoid = get_contador_sucdiv('ACC_ASIENTOS-ID-', '{}{}'.format(sucursalid, divisionid[-1]))
                    asiento_numero = get_contador_sucdiv('ACC_ASIENTOS-NUMBER-',
                                                         '{}{}'.format(sucursalid, divisionid[-1]))

                    fecha = datetime.datetime.strptime(json_data['fecha'], '%d/%m/%Y')
                    detalle = json_data['detalle']
                    cliente = json_data['cliente']

                    banco_ingreso = BanIngresos(
                        id=banco_ingresoid,
                        banco_id=json_data['bancoid'],
                        numero=banco_ingreso_numero,
                        asientoid=asientoid,
                        deudor_id=json_data['deudorid'],
                        fecha=fecha,
                        tipo=json_data['tipo'],
                        detalle=detalle,
                        valor=Decimal(json_data['valor']),
                        descuento=Decimal(json_data['descuento']),
                        financiero=Decimal(json_data['financiero']),
                        rfir=Decimal(json_data['rfir']),
                        rfiva=Decimal(json_data['rfiva']),
                        faltante=Decimal(json_data['faltante']),
                        sobrante=Decimal(json_data['sobrante']),
                        valor_base=Decimal(json_data['valor_base']),
                        nota=json_data['nota'],
                        divisionid=divisionid,
                        divisaid=divisaid,
                        cambio=Decimal(1.00),
                        sucursalid=sucursalid,
                        cajaid=json_data['cajaid'],
                        cobradorid=json_data['zonaid'],
                    )
                    banco_ingreso.save()

                    for item in json_data['pagos']:

                        if Decimal(item['valor']) > 0:
                            banco_ingreso_detid = get_contador_sucdiv('BAN_INGRESOS_DT-ID-',
                                                                      '{}{}'.format(sucursalid, divisionid[-1]))

                            banco_ingreso_det = BanIngresosDetalle(
                                id=banco_ingreso_detid,
                                ingreso_id=banco_ingreso.id,
                                tipo=item['tipo'],
                                numero=item['numero'],
                                banco=item['banco'],
                                cuenta=item['cuenta'],
                                fecha=fecha,
                                divisaid=divisaid,
                                cambio=Decimal(1.00),
                                valor=item['valor'],
                                valor_base=item['valor_base'],
                                sucursalid=sucursalid,
                                numcartilla=item['numcartilla'],
                                recibopago=item['recibo']
                            )
                            banco_ingreso_det.save()

                    for item in json_data['deuda']:
                        if Decimal(item['abono']) > 0:
                            banco_inreso_deuda = BanIngresosDeudas(
                                ingresoid=banco_ingreso.id,
                                deudaid=item['deudaid'],
                                divisaid=item['divisaid'],
                                cambiodia=Decimal(1.00),
                                saldo=item['saldo'],
                                valor=item['abono'],
                                dif_cambio=Decimal(0.00),
                                fecha=item['fecha'],
                                vencimiento=item['vencimiento'],
                                tipo=item['tipo'],
                                numero=item['numero'],
                                detalle=item['detalle'],
                                credito=item['credito'],
                                rubroid=item['rubroid'],
                                ctacxcid=item['ctacxid'],
                                cambio=item['cambio'],
                                divisionid=item['divisionid'],
                                sucursalid=sucursalid
                            )
                            banco_inreso_deuda.save()

                    asiento = AccAsientos(
                        id=asientoid,
                        numero=asiento_numero,
                        documentoid=banco_ingreso.id,
                        fecha=fecha,
                        tipo=json_data['tipo'],
                        detalle=detalle,
                        nota=json_data['nota'],
                        divisionid=divisionid,
                        sucursalid=sucursalid
                    )
                    asiento.save()

                    banco = BanBancos.objects.get(id=json_data['bancoid'])
                    # Asiento contable DEBE
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                asiento.id,
                                banco.ctamayorid,
                                detalle,
                                True,
                                divisaid,
                                Decimal(1.00),
                                json_data['valor'],
                                json_data['valor_base'],
                                request.user.username,
                                sucursalid,
                                ''
                            ))

                    # Asiento contable HABER
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "{CALL ACC_AsientosDT_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}", (
                                asiento.id,
                                json_data['ctacxid'],
                                detalle,
                                False,
                                divisaid,
                                Decimal(1.00),
                                json_data['valor'],
                                json_data['valor_base'],
                                request.user.username,
                                sucursalid,
                                ''
                            ))

                    for item in json_data['deuda']:

                        if Decimal(item['abono']) > 0:
                            cliente_deudaid = get_contador_sucdiv('CLI_CLIENTES_DEUDAS-ID-',
                                                                  '{}{}'.format(sucursalid, divisionid[-1]))

                            valor_base = round(Decimal(item['abono']) * Decimal(1.00), 2)
                            vencimiento = datetime.datetime.strptime(item['vencimiento'], '%Y-%m-%d')

                            with connection.cursor() as cursor:
                                cursor.execute(
                                    "{CALL CLI_ClientesDeudas_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                                    (
                                        cliente_deudaid,
                                        item['clienteid'],
                                        banco_ingresoid,
                                        asientoid,
                                        banco_ingreso_numero,
                                        detalle,
                                        item['abono'],
                                        valor_base,
                                        fecha,
                                        vencimiento,
                                        item['rubroid'],
                                        item['ctacxid'],
                                        item['divisaid'],
                                        item['cambio'],
                                        Decimal(0.00),
                                        json_data['tipo'],
                                        True,
                                        item['deudaid'],
                                        cliente['vendid'],
                                        False,
                                        item['divisionid'],
                                        request.user.username,
                                        sucursalid,
                                        '',
                                        item['numcartilla']
                                    ))

                    banco_kerdexid = get_contador_sucdiv('BAN_BANCOS_CARDEX-ID-',
                                                         '{}{}'.format(sucursalid, divisionid[-1]))

                    with connection.cursor() as cursor:
                        cursor.execute(
                            "{CALL BAN_BancosCardex_Insert(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)}",
                            (
                                banco_kerdexid,
                                json_data['bancoid'],
                                banco_ingresoid,
                                banco_ingreso_numero,
                                fecha,
                                json_data['tipo'],
                                '',
                                fecha,
                                '',
                                detalle,
                                divisaid,
                                Decimal(1.00),
                                True,
                                json_data['valor'],
                                json_data['valor_base'],
                                divisionid,
                                request.user.username,
                                sucursalid,
                                ''
                            ))

                    data['resp'] = True
                    return JsonResponse(data, status=200)

        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, status=200)

    def get(self, request, *args, **kwargs):
        data = {}
        addUserData(request, data)
        try:
            banco = request.user.segusuarioparametro.banco
            if banco is None:
                raise Exception("No se encontro cuenta banco asociado al usuario.")

            data['banco_id'] = banco.id
            data['sucursal'] = SisSucursales.objects.get(codigo=banco.sucursal)

            data['bancos'] = BanBancos.objects.filter(
                anulado=False,
                # clase__in=('01',)
            )
            data['zonas'] = SisZonas.objects.filter(
                anulado=False,
                tipo='Zonas'
            )
            if not request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                data['disabled'] = True

            return render(request, 'cliente/cli_documento_ingresos.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')

class CliClienteDeudaCartilla(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        data = {}
        addUserData(request, data)
        try:
            accion = request.GET.get('accion')

            if accion == 'estado_cuenta':
                criterio = {
                    'numcartilla': self.request.GET.get('cartilla', ''),
                    'cliente_id': self.request.GET.get('clienteid', '')
                }

                def queries(filters):
                    return [Q(**{k: v}) for k, v in filters.items() if v]

                factura = VenFacturas.objects.filter(
                    Q(anulado=False),
                    *queries(criterio)
                )[0]

                detalle_deuda = CliClientesDeudas.objects.filter(
                    Q(anulado=False),
                    *queries(criterio)
                ).order_by('fecha')

                total_debe = detalle_deuda.filter(credito=False).aggregate(debe=Sum('valor'))['debe']
                total_haber = detalle_deuda.filter(credito=True).aggregate(haber=Sum('valor'))['haber']

                total_debe = Decimal(total_debe) if total_debe is not None else Decimal(0.00)
                total_haber = Decimal(total_haber) if total_haber is not None else Decimal(0.00)

                saldo = round(total_debe - total_haber, 2)

                data['total_debe'] = total_debe
                data['total_haber'] = total_haber
                data['saldo'] = saldo

                data['detalle_deuda'] = detalle_deuda
                data['cartilla'] = self.request.GET.get('cartilla', '')
                data['clicodigo'] = factura.cliente.codigo
                data['cliente'] = factura.cliente.nombre

        except:
            messages.add_message(request, 40, 'Numero de cartilla no existe.')
        return render(request, 'cliente/cli_estado_cuenta_cartilla.html', data)

class CliClientesListView(LoginRequiredMixin, ListView):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    model = CliClientes
    template_name = 'cliente/cli_clientes_lista.html'  # Default: <app_label>/<model_name>_list.html
    context_object_name = 'clientes'  # Default: object_list
    paginate_by = 10
    creadopor = ''
    disabled = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        addUserData(self.request, context)
        s = self.request.GET.get('s', '')
        divisionid = self.request.GET.get('divisionid', '')
        sucursalid = self.request.GET.get('sucursalid', '')

        context['url'] = '&s={}&divisionid={}&sucursalid={}&creadopor={}'.format(
            s, divisionid, sucursalid, self.creadopor
        )
        context['s'] = s
        context['divisionid'] = divisionid
        context['creadopor'] = self.creadopor
        context['disabled'] = self.disabled
        context['sucursalid'] = sucursalid
        context['divisiones'] = SisDivisiones.objects.filter(anulado=False)
        context['sucursales'] = SisSucursales.objects.filter(anulado=False)
        context['usuarios'] = User.objects.filter(is_active=True)

        return context

    def get_queryset(self, **kwargs):
        search = self.request.GET.get('s', '')
        criterio = {
            'division_id': self.request.GET.get('divisionid', ''),
            'sucursalid': self.request.GET.get('sucursalid', ''),
            'creadopor': self.request.GET.get('creadopor', '')
        }
        if not self.request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
            criterio['creadopor'] = self.request.user.username
            self.disabled = True

        if search:
            criterio['creadopor'] = ''

        self.creadopor = criterio['creadopor']

        def queries(filters):
            return [Q(**{k: v}) for k, v in filters.items() if v]

        return CliClientes.objects.filter(
            Q(anulado=False),
            Q(ruc__icontains=search) |
            Q(nombre__icontains=search) |
            Q(codigo__icontains=search),
            *queries(criterio)
        ).order_by('-creadodate', '-editadodate')

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def cli_cliente_crear(request, template_name='cliente/cli_cliente_fichero.html'):
    if request.method == 'POST':
        try:
            form = CliClientesForm(request.POST, request.FILES)
            if form.is_valid():
                ruc = form.cleaned_data['ruc']
                if not CliClientes.objects.filter(anulado=False, ruc__icontains=ruc[:10]).exists():
                    form.save()
                    return redirect('/cliente/clientes/')
                else:
                    messages.add_message(request, 40, 'Número de Ruc ya se encuentra registrado en el sistema.')
        except Exception as e:
            messages.add_message(request, 40, str(e))
    else:
        form = CliClientesForm()

    data = {'accion': 'Crear'}
    addUserData(request, data)
    data['form'] = form
    data['ciudades'] = SisZonas.objects.filter(anulado=False, tipo='CIUDAD')
    data['zonas'] = SisZonas.objects.filter(anulado=False, tipo='ZONAS')
    data['vendedores'] = EmpEmpleados.objects.filter(anulado=False, vendedor=True)
    data['dias_semana'] = DIAS_SEMANA
    return render(request, template_name, data)

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def cli_cliente_editar(request, pk, template_name='cliente/cli_cliente_fichero.html'):
    try:
        cliente = CliClientes.objects.filter(pk=pk, anulado=False).exclude(pk='0000000001').first()
    except cliente.DoesNotExist:
        raise Http404("Cliente no se permite editar o no existe..")

    if not request.session['grupoid'] in USER_ALL_PERMISOS:
        if request.user.segusuarioparametro.empleado_id != '0000000045':
            if cliente.vendedor_id != request.user.segusuarioparametro.empleado_id:
                return redirect('/cliente/clientes/')

    if request.method == 'POST':
        try:
            form = CliClientesForm(request.POST, request.FILES, instance=cliente)
            if form.is_valid():
                ruc = form.cleaned_data['ruc']
                if not CliClientes.objects.filter(anulado=False, ruc=ruc[:10]).exclude(id=cliente.id).exists():
                    form.save()
                    return redirect('/cliente/clientes/')
                else:
                    messages.add_message(request, 40, 'Número de Ruc ya se encuentra registrado en el sistema.')
        except Exception as e:
            messages.add_message(request, 40, str(e))
    else:
        form = CliClientesForm(instance=cliente)

    data = {'accion': 'Editar'}
    addUserData(request, data)
    data['form'] = form
    data['cliente'] = cliente
    data['ciudades'] = SisZonas.objects.filter(anulado=False, tipo='CIUDAD')
    data['zonas'] = SisZonas.objects.filter(anulado=False, tipo='ZONAS')
    data['vendedores'] = EmpEmpleados.objects.filter(anulado=False, vendedor=True)
    data['dias_semana'] = DIAS_SEMANA
    return render(request, template_name, data)

class CliClienteCrear(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        accion = request.POST['accion']
        try:
            if accion == 'guardar':
                if not CliClientes.objects.filter(anulado=False, ruc__icontains=request.POST.get('ruc').strip()[:10]).exists():
                    with transaction.atomic():
                        cliente = CliClientes(
                            ruc=request.POST.get('ruc',''),
                            nombre=request.POST.get('nombres',''),
                            grupo_id= request.POST.get('grupo_id',''),
                            zona_id=request.POST.get('zonaid',''),
                            secuenciaid='0000000001',
                            vendedor_id='0000000001',
                            division_id=request.POST.get('divisionid',''),
                            clase=request.POST.get('clase',''),
                            termino=request.POST.get('terminoid',''),
                            forma_pago=request.POST.get('formapago',''),
                            direccion=request.POST.get('direccion',''),
                            telefono1=request.POST.get('telefono',''),
                            ciudad=request.POST.get('ciudad',''),
                            fecha=datetime.datetime.now(),
                            email=request.POST.get('email','')
                        )
                        cliente.save()
                        data['resp'] =True
                        data['cliente'] = {
                            'id':cliente.id,
                            'ruc': cliente.ruc
                        }
                        return JsonResponse(data, status=200)
                else:
                    raise Exception("El ruc o número de indenficicación ya se ecuentra registrado en el Sistema.")
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, status=200)
