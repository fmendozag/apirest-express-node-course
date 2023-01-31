import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.db.models import Q
from sistema.constantes import ESTADO_TRANSFERENCIA, TIPO_TRANSFERENCIA
from sistema.funciones import addUserData
from inventario.models import InvTransferencias, InvBodegas
from sistema.models import SisDivisiones
from django.http import Http404
from sistema.constantes import USER_ALL_PERMISOS, NOMBRE_SISTEMA, LOGO_INFORME_CABECERA, \
    NOMBRE_INSTITUCION, INSTITUCION_CIUDAD, INSTITUCION_DIRECCION, INSTITUCION_DIRECCION2, INSTITUCION_TELEFONO
from django.shortcuts import redirect
from easy_pdf.rendering import render_to_pdf_response

class InformeTranferenciaView(LoginRequiredMixin,ListView):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    model = InvTransferencias
    template_name = 'informe/inventario/inv_informe_transferencia.html'  # Default: <app_label>/<model_name>_list.html
    context_object_name = 'transferencias'  # Default: object_list
    paginate_by = 20
    creadopor = ''
    disabled = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        addUserData(self.request, context)
        qs = kwargs.pop('transferencias', self.object_list)

        s = self.request.GET.get('s', '')
        divisionid = self.request.GET.get('divisionid', '')
        tipo = self.request.GET.get('tipo', '')
        bodegaid = self.request.GET.get('bodegaid', '')
        estado_transferencia = self.request.GET.get('estado_transferencia', '')

        inicio = self.request.GET.get('inicio', '')
        final = self.request.GET.get('final', '')

        url = '&s={}&inicio={}&final={}&divisionid={}&creadopor={}&estado_transferencia={}&tipo={}&bodegaid={}'.format(
          s,inicio, final,divisionid,self.creadopor,estado_transferencia,tipo,bodegaid
        )
        context['url'] = url
        context['s'] = s
        context['inicio'] = inicio
        context['final'] = final
        context['divisionid'] = divisionid
        context['bodegaid'] = bodegaid
        context['tipo'] = tipo
        context['creadopor'] = self.creadopor
        context['disabled'] = self.disabled
        context['estado_transferencia'] = estado_transferencia

        context['usuarios'] = User.objects.filter(is_active=True)
        context['divisiones'] = SisDivisiones.objects.filter(anulado=False)
        context['estado_transferencias'] = ESTADO_TRANSFERENCIA
        context['tipos_transferencias'] = TIPO_TRANSFERENCIA
        context['bodegas'] = InvBodegas.objects.filter(anulado=False)

        if self.request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
            context['permiso'] = True

        return context

    def get_queryset(self, **kwargs):
        search = self.request.GET.get('s', '')
        criterio = {
            'division_id': self.request.GET.get('divisionid', ''),
            'creadopor': self.request.GET.get('creadopor', ''),
            'estado': self.request.GET.get('estado_transferencia', ''),
            'tipo': self.request.GET.get('tipo', ''),
            'bodega_origen_id': self.request.GET.get('bodegaid', '')
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

        return InvTransferencias.objects.filter(
            Q(anulado=False),
            Q(numero__icontains=search),
            *queries(criterio)
        )

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def transferencia_inv_documento(request,tipo,pid,name):
    if request.method == 'GET':
        data = {}
        try:
            try:
                transferencia = InvTransferencias.objects.get(pk=pid,anulado=False)
            except:
                raise Http404("Fallido!, No se encontró registro de transferencia")

            data['title'] = 'Documento orden de pedido'
            data['sistema'] = NOMBRE_SISTEMA
            data['logo_cabecera'] = LOGO_INFORME_CABECERA
            data['belbry'] = NOMBRE_INSTITUCION
            data['ciudad'] = INSTITUCION_CIUDAD
            data['direccion'] = INSTITUCION_DIRECCION
            data['direccion2'] = INSTITUCION_DIRECCION2
            data['telefono'] = INSTITUCION_TELEFONO
            data['hoy'] = datetime.datetime.now()
            data['transferencia'] = transferencia
            data['usuario'] = request.user.username
            data['titulo'] = 'Comprobante de Transferencia'

            if tipo == 'pdf':
                if request.user.groups.filter(id__in=USER_ALL_PERMISOS).exists():
                    return render_to_pdf_response(request,"informe/inventario/inv_informe_transferencia_pdf_adm.html", data)
                else:
                    return render_to_pdf_response(request, "informe/inventario/inv_informe_transferencia_pdf.html",data)
        except:
            raise
    return redirect('/')
