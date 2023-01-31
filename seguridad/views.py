from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from sistema.funciones import addUserData

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def index(request):
    data = {}
    addUserData(request, data)
    return render(request, 'seguridad/index.html', data)
