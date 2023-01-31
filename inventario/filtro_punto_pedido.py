from decimal import Decimal
from django.http import JsonResponse
from inventario.models import InvProductosEmpaques, InvProductosPrecios
from sistema.constantes import UBICACION_ID

def get_punto_pedido_empaques(request):
    data = {'resp': False, 'error': ''}
    if request.method == 'GET':
        try:
            accion = request.GET.get('accion', '')

            if accion == 'producto-codigo-barra':
                try:
                    pe = InvProductosEmpaques.objects.get(producto__anulado=False,codigo_barra=request.GET.get('codigo'),producto__ubicacionid=UBICACION_ID)
                except:
                    raise Exception("No se encontro el producto ingresado..")

                data['producto'] = {
                    "productoid": pe.producto_id,
                    "codigo": pe.codigo_barra.strip(),
                    "empaque": pe.nombre.strip(),
                    "factor": round(pe.factor, 2),
                    "precio": 0,
                    "precio_final": 0,
                    "precio_factor": 0,
                    "nombre": pe.producto.nombre.strip(),
                    "nombre_corto": pe.producto.nombre_corto.strip(),
                    "clase": pe.producto.clase,
                    "grupo_id": pe.producto.grupo_id.strip(),
                    "metodo": pe.producto.metodo.strip(),
                    "impuestoid": pe.producto.impuestoid.strip(),
                    "coniva": True if pe.producto.impuestoid.strip() else False,
                    "costo_compra": round(pe.producto.costo_compra, 4),
                    "vendible": pe.producto.vendible,
                    "comision_contado": round(pe.producto.web_comision_contado,2) if pe.producto.web_comision_contado is not None else 0,
                    "comision_credito":  round(pe.producto.web_comision_credito,2) if pe.producto.web_comision_credito is not None else 0,
                    "balanza": pe.producto.balanza,
                    "formato": pe.producto.descripcion,
                    "tasa_descuento_contado": round(pe.producto.ptg_descuento,2) if pe.producto.ptg_descuento is not None else 0,
                    "tasa_descuento_credito": round(pe.producto.ptg_descuento1,2) if pe.producto.ptg_descuento1 is not None else 0
                }
                data['resp'] = True
                return JsonResponse(data, status=200)

            elif accion == 'p-buscar-nombre':
                bodegaid = request.GET.get('bodegaid', '')
                sucursalid = request.GET.get('sucursalid', '')
                s = '%{}%'.format(request.GET.get('criterio', ''))

                producto_empaques = InvProductosEmpaques.objects.filter(
                    producto__anulado=False,
                    producto__ubicacionid=UBICACION_ID
                ).extra(
                    where=["UPPER([INV_PRODUCTOS].[Nombre]) LIKE UPPER(%s)"], params=[s]
                ).exclude(codigo_barra='').order_by('producto__nombre', 'nombre')[:30]

                lista_productos = []
                for pe in producto_empaques:
                    stock = 0
                    try:
                        producto_stock = pe.producto.get_bodega_stock(bodegaid, sucursalid)
                        if producto_stock is not None:
                            stock = round(producto_stock['stock'], 2)
                    except:
                        pass
                    lista_productos.append({
                        "productoid": pe.producto_id,
                        "codigo": pe.codigo_barra,
                        "empaque": pe.nombre,
                        "factor": pe.factor,
                        "formato": pe.producto.descripcion,
                        "nombre": pe.producto.nombre,
                        "costo_compra": round(pe.producto.costo_compra, 4),
                        "precio_und": round(pe.producto.precio4, 2),
                        "precio_cja": round(pe.producto.precio3, 2),
                        "precio_cja_factor": round(pe.producto.precio1, 2),
                        "stock": stock
                    })

                data['productos'] = lista_productos
                data['resp'] = True
                return JsonResponse(data, status=200)

            elif accion == 'p-buscar-rango':

                stock = Decimal('0.00')
                productoid = request.GET.get('productoid')
                cantidad = Decimal(request.GET.get('cantidad','1'))
                factor = Decimal(request.GET.get('factor','1'))
                precio_lista = request.GET.get('precio_lista', '1')
                bodegaid = request.GET.get('bodegaid')
                #balanza = bool(int(request.GET.get('balanza', 0)))
                sucursalid = request.GET.get('sucursalid')
                controla_stock = bool(int(request.GET.get('controla_stock', 0)))

                if (factor * cantidad) < 1:
                    rangos = InvProductosPrecios.objects.filter(producto_id=productoid,rango1__lte=factor,rango2__gte=factor).order_by('rango1')
                else:
                    parte_decimal = factor % 1
                    if parte_decimal > 0:
                        rangos = InvProductosPrecios.objects.filter(producto_id=productoid,rango1__lte=(factor * cantidad),rango2__gte=(factor * cantidad)).order_by('rango1')
                    else:
                        rangos = InvProductosPrecios.objects.filter(producto_id=productoid,rango1__lte=int(factor * cantidad),rango2__gte=int(factor * cantidad)).order_by('rango1')

                if rangos.exists():
                    rango = rangos[0]
                    if controla_stock:
                        cantidad_cotiza = Decimal(request.GET.get('cantidad_cotiza', 0))
                        producto_stock = rango.producto.get_bodega_stock(bodegaid, sucursalid)
                        if producto_stock is not None:
                            stock = producto_stock['stock']
                        if stock <= 0:
                            raise Exception("El producto se encuentra Sin stock: {}-{}".format(rango.producto.codigo,rango.producto.nombre))
                        elif (cantidad_cotiza * factor) > stock:
                            raise Exception("La cantidad ingresada supera el stock: {}".format(stock))

                    precio = round(rango.precio,4)
                    precio_final = round(rango.precio_final, 4)

                    if precio_lista == '1':
                        precio_activo = request.GET.get('precio_activo', '2')
                        if precio_activo == '2':
                            precio = round(rango.precio_credito, 4)
                        elif precio_activo == '3':
                            precio = round(rango.precio_distribuidor, 4)
                        elif precio_activo == '4':
                            precio = round(rango.precio_mayorista, 4)

                    if precio <= 0.00:
                        raise Exception('El producto {}, no tiene PVP.'.format(rango.producto.nombre))
                    elif precio < rango.producto.costo_compra:
                        raise Exception('El PVP del producto {} es menor al Costo de compra..'.format(rango.producto.nombre))

                    precio_factor = round(precio * factor, 4)
                    data['producto'] = {
                        "productoid": rango.producto_id,
                        "precio": precio,
                        "precio_final": precio_final,
                        "precio_factor": precio_factor,
                        "stock": stock
                    }
                    data['resp'] = True
                    return JsonResponse(data, status=200)
                else:
                    raise Exception('No se encontró rangos para del producto seleccionado..')

            elif accion == 'p-buscar-autocomplete':
                s = '%{}%'.format(request.GET.get('criterio', ''))
                producto_empaques = InvProductosEmpaques.objects.filter(
                    producto__anulado=False,
                    producto__ubicacionid=UBICACION_ID
                ).extra(
                    where=["UPPER([INV_PRODUCTOS].[Nombre]) LIKE UPPER(%s)"], params=[s]
                ).exclude(codigo_barra='').order_by('producto__nombre', 'nombre')[:20]

                lista_productos = []
                for pe in producto_empaques:
                    lista_productos.append({
                        "productoid": pe.producto_id,
                        "codigo": pe.codigo_barra.strip(),
                        "nombre": '{} {} ({})'.format(pe.nombre.strip(),pe.producto.nombre,pe.producto.descripcion)
                    })
                return JsonResponse({"items": lista_productos}, status=200)
        except Exception as e:
            data['error'] = str(e)
    return JsonResponse(data, status=200)
