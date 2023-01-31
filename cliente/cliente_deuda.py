from django.db.models import Q, Sum
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic.base import View
from cliente.models import CliClientesDeudas
from empleado.models import EmpEmpleados
from sistema.funciones import addUserData

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def get_consulta_cliente_cartilla(request):
    data = {'resp': False, 'error': ''}
    if request.method == 'POST':
        try:
            accion = request.POST.get('accion')

            if accion == 'detalle_deuda_cartilla':
                num_cartilla = request.POST.get('numcartilla', None)

                if CliClientesDeudas.objects.filter(anulado=False,numcartilla=num_cartilla,saldo__gt=0,credito=False).exists():
                    cliente_deuda = CliClientesDeudas.objects.filter(anulado=False,numcartilla=num_cartilla,saldo__gt=0,credito=False).first()

                    try:
                        vendedor = EmpEmpleados.objects.get(id=cliente_deuda.vendedorid)
                    except:
                        vendedor = None

                    data['cliente'] = {
                        "documentoid": cliente_deuda.documentoid,
                        "clienteid": cliente_deuda.cliente.id,
                        "cod": cliente_deuda.cliente.codigo,
                        "ruc": cliente_deuda.cliente.ruc,
                        "nombre": cliente_deuda.cliente.nombre,
                        # "dia": factura.dia_cobro,
                        # "pago": factura.pagada,
                        "divisionid": cliente_deuda.cliente.division.id,
                        "division": cliente_deuda.cliente.division.nombre,
                        # "bodega": cliente_deuda.bodega.id,
                        "tipo": cliente_deuda.tipo,
                        "total": cliente_deuda.valor,
                        "vendid": vendedor.id if vendedor is not None else '',
                        "vendcod": vendedor.codigo if vendedor is not None else '',
                        "vend": vendedor.nombre if vendedor is not None else '',
                        # "recaudador": recaudador.nombre if recaudador is not None else '',
                        # "entregador": entregador.nombre if entregador is not None else '',
                        "zonaid": cliente_deuda.cliente.zona.id if cliente_deuda.cliente.zona is not None else '',
                        "zona": cliente_deuda.cliente.zona.nombre if cliente_deuda.cliente.zona is not None else '',
                        "numcartilla": cliente_deuda.numcartilla
                    }

                    lista_deudas = []
                    for d in CliClientesDeudas.objects.filter(anulado=False,cliente_id=cliente_deuda.cliente.id,
                                                              numcartilla=num_cartilla, saldo__gt=0,credito=False):
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
    return JsonResponse(data, status=200)

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

                detalle_deuda = CliClientesDeudas.objects.filter(
                    Q(anulado=False),
                    *queries(criterio)
                ).order_by('fecha')

                cliente_deuda = detalle_deuda.first()

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
                data['clicodigo'] = cliente_deuda.cliente.codigo
                data['cliente'] = cliente_deuda.cliente.nombre

        except:
            messages.add_message(request, 40, 'Numero de cartilla no existe.')
        return render(request, 'cliente/cli_estado_cuenta_cartilla.html', data)