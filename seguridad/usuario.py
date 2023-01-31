from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from sistema.constantes import SISTEMA_AUTOR, LOGO_SISTEMA, NOMBRE_SISTEMA

class LoginView(View):
    def post(self, request, *args, **kwargs):
        data = {'resp': False}
        try:
            norobot = request.POST.get('norobot','')
            if not norobot:
                raise Exception("Login Fallido!, acceso No autorizado.")

            user = authenticate(username=request.POST['usuario'],password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    data['resp'] = True
                    data['user'] = user.username
                    return JsonResponse(data, status=200)
                else:
                    data['error'] = 'Login Fallido!, usuario no esta habilitado'
            else:
                data['error'] = 'Login Fallido!, credenciales incorrectas.'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, status=200)

class LoginPageView(TemplateView):
    template_name = 'seguridad/login.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['autor'] = SISTEMA_AUTOR
        context['titulo'] = 'Inicio de Sesión'
        context['logo_sistema'] = LOGO_SISTEMA
        context['nombre_sistema'] = NOMBRE_SISTEMA
        return context

class ConsultaCuenta(View):
    def post(self, request, *args, **kwargs):
        data = {'resp': False}
        try:
            norobot = request.POST.get('norobot', '')
            if not norobot:
                raise Exception("Login Fallido!, acceso No autorizado.")

            cedula = request.POST.get('cedula','')
            if cedula:
                # p = CatPersona.objects.get(cedula=cedula,anulado=False)
                # if p is not None:
                #     if p.email_institucional:
                #         data['email'] = p.email_institucional
                #         data['resp']=True
                        return JsonResponse(data, status=200)
            data['error'] = "La cuenta institucional ingresada no Existe."
        except Exception as e:
            data['error'] = "La cuenta institucional ingresada no Existe."
        return JsonResponse(data, status=200)

def logout_user(request):
    logout(request)
    return redirect('/seguridad/login/')

