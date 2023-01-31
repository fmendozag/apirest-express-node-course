from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.base import View

from sistema.funciones import addUserData


class CambiarPasswordInterno(LoginRequiredMixin,View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False}
        try:
            accion = request.POST['accion']
            if accion == 'cambio-password-interno':
                norobot = request.POST.get('norobot', '')
                if not norobot:
                    raise Exception("Login Fallido!, acceso No autorizado.")

                user = authenticate(username=request.user.username, password=str(request.POST['password_actual']))
                if user is not None:
                    user.set_password(str(request.POST['password_nueva']))
                    user.save()
                    data['resp'] = True
                    return JsonResponse(data, status=200)
                else:
                    data['error'] = 'Login Fallido!, credenciales incorrectas.'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, status=200)

    def get(self, request, *args, **kwargs):
        data = {}
        addUserData(request, data)
        return render(request,'seguridad/cambiar_password_interno.html',data)
