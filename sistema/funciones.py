import datetime
from django.shortcuts import redirect
from django.http import Http404
from sistema.constantes import LOGO_SISTEMA, NOMBRE_SISTEMA

def addUserData(request, data):
    if request.method == 'GET':
        try:
            data['hoy'] = datetime.datetime.now()
            data['usuario'] = request.user
            data['logo_sistema'] = LOGO_SISTEMA
            data['nombre_sistema'] = NOMBRE_SISTEMA
            data['user_grupos'] = request.user.groups.all()
        except:
            pass
        # try:
        #     data['persona'] = persona = CatPersona.objects.get(anulado=False, usuario=request.user)
        # except:
        #     persona = None
        try:
            if 'gpid' in request.GET:
                grupo_id = int(request.GET['gpid'])
                try:
                    grupos = request.user.groups.filter(id=grupo_id)
                    if grupos.exists():
                        grupo = request.user.groups.filter(id=grupo_id)[0]
                        request.session['grupoid'] = grupo.id
                except:
                    raise Http404
                    return redirect('/', error='error messsage')

            elif not 'grupoid' in request.session:
                if len(data['user_grupos']):
                    grupo = data['user_grupos'][0]
                    request.session['grupoid'] = grupo.id
        except:
            pass
        if 'grupoid' in request.session:
            try:
                grupo = request.user.groups.get(pk=request.session['grupoid'])
                data['grupo'] = grupo
                data['modulos_grupos'] = grupo.segmodulogrupo_set.filter(activo=True).order_by('prioridad')
            except:
                pass
