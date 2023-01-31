from decimal import Decimal
from django.http import JsonResponse
from inventario.models import InvProductosEmpaques, InvProductosPrecios, InvProductos
from sistema.constantes import UBICACION_ID

def get_productos_empaque(request):
    data = {'resp': False, 'error': ''}
    if request.method == 'GET':
        try:
            accion = request.GET.get('accion', '')
            if accion == 'p-codigo-barra':
                cantidad = Decimal(request.GET.get('cantidad','1'))
                precio = Decimal('0.00')
                precio_final = Decimal('0.00')
                precio_factor = Decimal('0.00')
                stock = Decimal('0.00')
                precio_lista = request.GET.get('precio_lista','1')
                bodegaid = request.GET.get('bodegaid')
                sucursalid = request.GET.get('sucursalid')
                try:
                    pe = InvProductosEmpaques.objects.get(producto__anulado=False,codigo_barra=request.GET.get('codigo'),producto__ubicacionid=UBICACION_ID)
                except:
                    raise Exception("No se encontro el producto ingresado..")

                factor = round(pe.factor, 2)
                producto_stock = pe.producto.get_bodega_stock(bodegaid,sucursalid)
                
                if producto_stock is not None:
                    stock = producto_stock['stock']

                if stock <= 0:
                    raise Exception("El producto se encuentra Sin stock: {}".format(pe.producto.codigo))
                elif pe.producto.balanza and cantidad > stock:
                    cantidad = cantidad - stock

                if (cantidad * factor) > stock:
                    raise Exception("El producto no tiene Stock suficiente: {} Actual".format(stock))

                rangos = InvProductosPrecios.objects.filter(producto_id=pe.producto_id, rango1__lte=factor,rango2__gte=factor)

                if rangos.exists():
                    rango = rangos[0]
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
                else:
                    precio = round(pe.precio, 4)
                    precio_final = round(pe.producto.precio4, 4)
                    if precio_lista == '1':
                        precio_activo = request.GET.get('precio_activo', '2')
                        if precio_activo == '2':
                            precio = round(pe.credito, 4)
                        elif precio_activo == '3':
                            precio = round(pe.distribuidor, 4)
                        elif precio_activo == '4':
                            precio = round(pe.mayorista, 4)

                precio_factor = round(precio * factor, 4)
                ccontado = pe.producto.web_comision_contado
                ccredito = pe.producto.web_comision_credito

                data['producto'] = {
                    "productoid": pe.producto_id,
                    "codigo": pe.codigo_barra.strip(),
                    "empaque": pe.nombre.strip(),
                    "factor": factor,
                    "precio": precio,
                    "precio_final": precio_final,
                    "precio_factor": precio_factor,
                    "nombre": pe.producto.nombre.strip(),
                    "nombre_corto": pe.producto.nombre_corto.strip(),
                    "clase": pe.producto.clase,
                    "grupo_id": pe.producto.grupo_id.strip(),
                    "ctamayor_id": pe.producto.ctamayor.id,
                    "ctaventa_id": pe.producto.ctaventas_id,
                    "ctacosto_id": pe.producto.ctacostos_id,
                    "ctadescuento_id": pe.producto.ctadescuento_id,
                    "ctadescuento_id": pe.producto.ctadescuento_id,
                    "ctadevolucion_id": pe.producto.ctadevolucion_id,
                    "metodo": pe.producto.metodo.strip(),
                    "impuestoid": pe.producto.impuestoid.strip(),
                    "coniva": True if pe.producto.impuestoid.strip() else False,
                    "costo_compra": round(pe.producto.costo_compra,4),
                    "vendible": pe.producto.vendible,
                    "cantidad": 1,
                    "comision_contado": ccontado if ccontado is not None else 0,
                    "comision_credito": ccredito if ccredito is not None else 0,
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
                ).exclude(codigo_barra='').order_by('producto__nombre','nombre')[:20]

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
                balanza = request.GET.get('balanza', '0')
                bodegaid = request.GET.get('bodegaid')
                sucursalid = request.GET.get('sucursalid')

                if balanza == '1' and cantidad < 1:
                    rangos = InvProductosPrecios.objects.filter(producto_id=productoid,rango1__lte=factor,rango2__gte=factor)
                else:
                    rangos = InvProductosPrecios.objects.filter(producto_id=productoid,rango1__lte=int(factor * cantidad),rango2__gte=int(factor * cantidad))

                if rangos.exists():
                    rango = rangos[0]
                    producto_stock = rango.producto.get_bodega_stock(bodegaid, sucursalid)
                    if producto_stock is not None:
                        stock = producto_stock['stock']

                    if stock <= 0:
                        raise Exception("El producto se encuentra sin stock en bodega: {}".format(producto_stock['bodega__nombre']))
                    elif (cantidad * factor) > stock:
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
                else:
                    precio = Decimal('0.00')
                    precio_final = Decimal('0.00')

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

            elif accion == 'p-productoid-stock':
                stock = Decimal('0.00')
                bodegaid = request.GET.get('bodegaid')
                sucursalid = request.GET.get('sucursalid')
                try:
                    producto = InvProductos.objects.get(pk=request.GET.get('productoid'))
                    producto_stock = producto.get_bodega_stock(bodegaid, sucursalid)
                    if producto_stock is not None:
                        stock = round(producto_stock['stock'],2)

                    data['stock'] = stock
                    data['resp'] = True
                    return JsonResponse(data, status=200)
                except:
                    raise Exception("No se encontro Stock del producto..")

        except Exception as e:
            data['error'] = str(e)
    return JsonResponse(data, status=200)
