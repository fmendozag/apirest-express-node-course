from uuid import uuid4

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic.base import View

class SolicitudCambioClave(View):
    def post(self, request, *args, **kwargs):
        data = {'resp': False}
        try:
            norobot = request.POST.get('norobot', '')
            if not norobot:
                raise Exception("Fallido!, acceso No autorizado.")

            cedula = request.POST.get('cedula', '')
            # if cedula:
            #     p = CatPersona.objects.get(cedula=cedula, anulado=False)
            #     if p is not None:
            #         if p.email_institucional:
            #             p.token = uuid4()
            #             p.save()
            #             parametros ='{}/{}/{}/'.format(p.id,p.cedula,p.token)
            #             reseptores = [p.email_institucional]
            #             render_to_revisor_email(
            #                 asunto='SOLICITUD DE CAMBIO DE CONTRASEÑA EN SAyA',
            #                 body={
            #                     'persona': p,
            #                     'url_saya': '{}{}{}'.format(URL_SAYA,'seguridad/solicitud-cambio-clave-form/',parametros)
            #                 },
            #                 receptores=reseptores,
            #                 template='email/solicitud_cambio_clave_email.html'
            #             )
            #             data['email'] = p.email_institucional
            #             data['resp'] = True
            #             return JsonResponse(data, status=200)
            data['error'] = "No se encontró información para el número de cédula ingresado.."
        except Exception as e:
            data['error'] = "No se encontró información para el número de cédula ingresado.."
        return JsonResponse(data, status=200)

class UsuarioCambiarClave(View):
    def post(self, request, *args, **kwargs):
        data = {'resp': False}
        try:
            norobot = request.POST.get('norobot', '')
            if not norobot:
                raise Exception("Fallido!, acceso No autorizado.")

            # persona = CatPersona.objects.get(pk=request.POST.get('estudiante_id'))
            # if persona.usuario is not None:
            #     usuario = persona.usuario
            #     if usuario.is_active:
            #         usuario.set_password(str(request.POST.get('password')))
            #         usuario.save()
            #         data['resp']=True
            #         return JsonResponse(data, status=200)

            data['error'] = "La cuenta de usuario no se encuentra habilitada.."
        except Exception as e:
            data['error'] = "No se encontró información cuenta de usuario del estudiante vuelva a intentarlo.."
        return JsonResponse(data, status=200)

def solicitar_cambio_clave_form(request,id,ced,token):
    try:
        data={}
        # if CatPersona.objects.filter(anulado=False,cedula=ced,token=token).exists():
        #     data['persona'] = CatPersona.objects.get(pk=id)
        #     return render(request, 'seguridad/solicitud_cambio_clave.html', data)
    except Exception as e:
        pass
    return redirect('/')





