from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from seguridad.models import SegUsuarioParametro
class SegAutorizacionView(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        try:
            accion = request.POST.get('accion')
            if accion == 'pos-autorizacion':
                codigo_acceso = self.request.POST.get('codigo_acceso',None)
                user_parametro = SegUsuarioParametro.objects.filter(activo=True,codigo_acceso=codigo_acceso).first()
                if user_parametro is not None:
                    data['usuario']={
                        'usuario_id': user_parametro.usuario.id,
                        'username': user_parametro.usuario.username
                    }
                    data['resp'] = True
                else:
                    data['error'] = 'Autorización: Codigo de acceso es incorrecto..'
        except Exception as e:
            data['error'] = 'error: ' + str(e)
        return JsonResponse(data, status=200)
