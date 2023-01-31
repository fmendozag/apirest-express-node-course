from contadores.models import SisContadores
# def get_contador_sd(entidad,user):
#     user = get_current_user()
#     codigo = '{}-{}{}'.format(entidad,user.segusuarioparametro.banco.sucursal,user.segusuarioparametro.banco.division[:-1].strip())
#     contador = SisContadores.objects.get(codigo=codigo)
#     contador.valor +=1
#     contador.save()
#     return str(contador.valor).zfill(10)

def get_contador(entidad,user):
    sd = user.segusuarioparametro.banco.sucursal
    codigo = '{}-{}'.format(entidad,sd)
    contador = SisContadores.objects.filter(codigo=codigo).first()
    if contador is None:
        contador = SisContadores.objects.create(codigo=codigo,valor=0)
    contador.valor += 1
    contador.save()
    return sd + str(contador.valor).zfill(8)

def get_contador_sucdiv(entidad,sd):
    codigo = entidad + sd
    contador = SisContadores.objects.filter(codigo=codigo).first()
    if contador is None:
        contador = SisContadores.objects.create(codigo=codigo,valor=0)
    contador.valor +=1
    contador.save()
    return sd + str(contador.valor).zfill(7)

def get_contador_sucuencia_preimpresa(codigo,serie):
    contador = SisContadores.objects.filter(codigo=codigo).first()
    if contador is None:
        contador = SisContadores.objects.create(codigo=codigo,valor=0)
    contador.valor +=1
    contador.save()
    return '{}-{}'.format(serie,str(contador.valor).zfill(9))

def get_contador_sucuencia_sri(codigo):
    contador = SisContadores.objects.filter(codigo=codigo).first()
    if contador is None:
        contador = SisContadores.objects.create(codigo=codigo,valor=0)
    contador.valor +=1
    contador.save()
    return str(contador.valor).zfill(9)
