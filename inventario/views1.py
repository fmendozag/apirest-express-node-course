import copy
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect

from inventario.models import InvPdBodegaStock, InvProductos, InvProductosEmpaques, InvProductosPrecios
from sistema.models import SisParametros


@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def get_consulta_producto(request):
    data = {'resp': False, 'error': ''}
    if request.method == 'POST':
        try:
            accion = request.POST.get('accion')
            if accion == 'producto_cod':
                try:
                    inv = InvPdBodegaStock.objects.filter(
                        producto__anulado=False,
                        stock__gt=0,
                        bodega_id=request.POST.get('bodega_id'),
                        producto__codigo=request.POST.get('codigo')
                    )[0]
                except:
                    raise Exception("No se encontró el codigo del producto.")

                tipo = request.POST.get('tipo')
                precio = Decimal('0.0')

                if inv.producto.grupo is not None:
                    grupo = inv.producto.grupo
                    costo = Decimal(inv.producto.costo_compra)
                    if tipo == '0':
                        try:
                            porc_rent_costo_credito = Decimal(grupo.rentabilidad_costo_credito)
                        except:
                            porc_rent_costo_credito = Decimal('0.0')

                        precio = round(costo + (costo * porc_rent_costo_credito / 100), 2)
                    else:
                        try:
                            porc_rent_costo_contado = Decimal(grupo.rentabilidad_costo_contado)
                        except:
                            porc_rent_costo_contado = Decimal('0.0')
                        precio = round(costo + (costo * porc_rent_costo_contado / 100), 2)

                try:
                    if inv.producto.impuestoid.strip():
                        precio = precio * Decimal('1.12')                                        

                except:
                    pass

                data['producto'] = {
                    "id": inv.producto.id,
                    "cod": inv.producto.codigo.strip(),
                    "producto": inv.producto.nombre.strip(),
                    "stock": inv.stock,
                    "precio": precio
                }
                data['resp'] = True
                return JsonResponse(data, status=200)

            if accion == 'producto_cod_all':
                try:
                    inv = InvPdBodegaStock.objects.filter(
                        producto__anulado=False,
                        stock__gt=0,
                        bodega_id=request.POST.get('bodega_id'),
                        producto__codigo=request.POST.get('codigo')
                    )[0]
                except:
                    raise Exception("No se encontró el codigo del producto.")

                try:
                    if inv.producto.impuestoid.strip():
                        paramatro = SisParametros.objects.get(id=inv.producto.impuestoid.strip())
                        tasaimpuesto = Decimal(paramatro.valor.strip())
                        cuentaid = paramatro.extradata.strip().replace('CuentaID=', '')
                        coniva = True
                    else:
                        tasaimpuesto = Decimal(0.00)
                        cuentaid = ''
                        coniva = False
                except:
                    tasaimpuesto = Decimal(0.00)
                    cuentaid = ''
                    coniva = False

                tipo = request.POST.get('tipo')
                porc_comi_pvp_contado = Decimal('0.0')
                porc_comi_pvp_credito = Decimal('0.0')
                rent_pvp_credito = Decimal('0.0')
                rent_pvp_contado = Decimal('0.0')
                precio = Decimal('0.0')

                if inv.producto.grupo is not None:
                    grupo = inv.producto.grupo
                    porc_rent_costo_contado = Decimal(grupo.rentabilidad_costo_contado)
                    porc_rent_costo_credito = Decimal(grupo.rentabilidad_costo_credito)
                    porc_comi_pvp_contado = Decimal(grupo.comision_pvp_contado)
                    porc_comi_pvp_credito = Decimal(grupo.comision_pvp_credito)

                    costo = Decimal(inv.producto.costo_compra)
                    if tipo == '0':
                        rent_pvp_credito = round(costo * (porc_rent_costo_credito / 100), 2)
                        precio = round(costo + (costo * porc_rent_costo_credito / 100), 2)
                    else:
                        rent_pvp_contado = round(costo * (porc_rent_costo_contado / 100), 2)
                        precio = round(costo + (costo * porc_rent_costo_contado / 100), 2)

                data['producto'] = {
                    "id": inv.producto.id,
                    "cod": inv.producto.codigo.strip(),
                    "producto": inv.producto.nombre.strip(),
                    "alias": inv.producto.nombre_corto.strip(),
                    "clase": inv.producto.clase.strip(),
                    "empaque": inv.producto.empaque.strip(),
                    "stock": inv.stock,
                    "precio": precio,
                    "costo": inv.producto.costo_compra,
                    "impuestoid": inv.producto.impuestoid.strip() if inv.producto.impuestoid is not None else '',
                    "coniva": coniva,
                    "tasaimpuesto": tasaimpuesto,
                    "cuentaid": cuentaid,
                    "porc_comi_pvp_contado": porc_comi_pvp_contado,
                    "porc_comi_pvp_credito": porc_comi_pvp_credito,
                    "comi_pvp_contado": 0,
                    "comi_pvp_credito": 0,
                    "rent_pvp_contado": rent_pvp_contado,
                    "rent_pvp_credito": rent_pvp_credito
                }
                data['resp'] = True
                return JsonResponse(data, status=200)
        except Exception as e:
            data['error'] = 'error: ' + str(e)
    else:
        try:
            accion = request.GET.get('accion')
            if accion == 'producto_buscar':
                criterio = request.GET.get('criterio', '')
                inventarios = InvPdBodegaStock.objects.filter(
                    Q(producto__anulado=False),
                    Q(stock__gt=0),
                    Q(bodega_id=request.GET.get('bodega_id')),
                    Q(producto__nombre__icontains=criterio)
                ).order_by('producto__nombre')[:15]

                lista_productos = []
                for inv in inventarios:
                    lista_productos.append({
                        "id": inv.producto.id,
                        "cod": inv.producto.codigo,
                        "producto": inv.producto.nombre,
                        "stock": inv.stock,
                        "precio": inv.producto.precio4,
                        "precio_credito": inv.producto.precio_credito1,
                        "costo": inv.producto.costo_promedio
                    })
                return JsonResponse({"items": lista_productos}, status=200)
        except Exception as e:
            data['error'] = 'error: ' + str(e)
    return JsonResponse(data, status=200)

def get_procesar_precios(request):
    data = {'resp': False, 'error': ''}
    if request.method == 'GET':
        try:
            with transaction.atomic():

                for p in InvProductos.objects.filter(anulado=False).exclude(
                    codigo__in=[
                    '000222',
                    '004177',
                    '000220',
                    '000891',
                    '000514',
                    '000516',
                    '003301',
                    '003387',
                    '000522',
                    '000494',
                    '000518',
                    '002109',
                    '000974',
                    '000617',
                    '000578',
                    '003335',
                    '003026',
                    '005529',
                    '005471',
                    '000521',
                    '000379',
                    '000233',
                    '000420',
                    '002462',
                    '000380',
                    '000795',
                    '000796',
                    '001787'
                ]):
                    lista_empaques = copy.copy(p.invproductosempaques_set.all().values())
                    p.invproductosempaques_set.all().delete()

                    for item in lista_empaques:
                        if p.costo_compra > 0:

                            costo = Decimal(p.costo_compra) * Decimal(item['factor'])
                            precio_cobertura = round(costo + (costo * Decimal('0.08')), 4)

                            pe = InvProductosEmpaques(
                                producto_id=item['producto_id'],
                                codigo=item['codigo'],
                                codigo_barra=item['codigo_barra'],
                                nombre=item['nombre'],
                                factor=item['factor'],
                                tasa_utilidad=item['tasa_utilidad'],
                                embarque=item['embarque'],
                                fijo=item['fijo'],
                                precio=item['precio'],
                                grupo=item['grupo'],
                                creadopor=item['creadopor'],
                                creadodate=item['creadodate'],
                                sucursalid=item['sucursalid'],
                                pcid=item['pcid'],
                                placa=item['placa'],
                                tasa_credito=item['tasa_credito'],
                                credito=precio_cobertura,
                                tasa_distribuidor=item['tasa_distribuidor'],
                                distribuidor=item['distribuidor'],
                                tasa_mayorista=item['tasa_mayorista'],
                                mayorista=item['mayorista'],
                            )
                            pe.save()

                    lista_precios = copy.copy(p.invproductosprecios_set.all().values())
                    p.invproductosprecios_set.all().delete()

                    for item in lista_precios:
                        costo = Decimal(p.costo_compra)
                        precio_cobertura = round(costo + (costo * Decimal('0.08')), 4)

                        pr = InvProductosPrecios(
                            producto_id=item['producto_id'],
                            rango1=item['rango1'],
                            rango2=item['rango2'],
                            precio=item['precio'],
                            precio_final=item['precio_final'],
                            precio_credito=precio_cobertura,
                            precio_distribuidor=item['precio_distribuidor'],
                            precio_mayorista=item['precio_mayorista'],
                            creadopor=item['creadopor'],
                            creadodate=item['creadodate'],
                            sucursalid=item['sucursalid'],
                            pcid=item['pcid']
                        )
                        pr.save()

        except Exception as e:
            messages.add_message(request, 40,str(e))
        return redirect('/')
