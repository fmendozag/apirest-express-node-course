from django.contrib.auth.models import Group
from django.shortcuts import redirect, render

from sistema.constantes import USER_ALL_PERMISOS
def unauthenticated_user(view_func):
    def wrapper_func(request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return view_func(request,*args,**kwargs)
    return wrapper_func

def permiso_modulo(allowed_roles=USER_ALL_PERMISOS):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            try:
                if request.session['grupoid'] in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    grupo = Group.objects.get(pk=request.session['grupoid'])
                    items = str(request.path).split('/')[1:]
                    url = '{}/{}/'.format(items[0],items[1])
                    if grupo.segmodulogrupo_set.filter(modulos__url=url).exists():
                        return view_func(request, *args, **kwargs)
                    else:
                        return render(request, 'seguridad/no_autorizado.html')
            except:
                return render(request, 'seguridad/no_autorizado.html')
        return wrapper_func
    return decorator


