import datetime
from decimal import Decimal
from django.db import transaction, connection
from django.db.models import Q, Sum, F
from django.db.models.functions import Coalesce
from rest_framework.response import Response
from rest_framework.views import APIView
from contadores.fn_contador import get_contador_sucdiv
from inventario.models import InvProductosEmpaques, InvProductos, InvTransferencias, InvTransferenciasDt, InvBodegas, \
    InvProductosPrecios, InvFisico, InvFisicoProductos
from sistema.models import SisParametros

class InvTransferencia(APIView):
    def post(self, request,accion,bodega_id, *args, **kwargs):
        data = {}
        try:
            if accion == 'guardar-pendientes':
                with transaction.atomic():
                    try:
                        inventario = self.request.user.segusuarioparametro.inventario
                        if inventario is None:
                            raise
                    except:
                        raise Exception("Invalido paramatros bodega destino..")

                    try:
                       bodega_origen = InvBodegas.objects.get(anulado=False,pk=bodega_id)
                    except:
                        raise Exception("No se encontro bodega de origen..")

                    fecha = datetime.date.today()
                    sucursalid = inventario.sucursal.codigo
                    divisionid = inventario.division.id
                    bodega_destino = inventario.bodega

                    tranferencia_id = get_contador_sucdiv('INV_TRANSFERENCIAS-ID-','{}{}'.format(sucursalid, divisionid[-1]))
                    tranferencia_numero = get_contador_sucdiv('INV_TRANSFERENCIAS-NUMBER-','{}{}'.format(sucursalid, divisionid[-1]))

                    tranferencia = InvTransferencias(
                        id=tranferencia_id,
                        numero=tranferencia_numero,
                        division_id=divisionid,
                        fecha=fecha,
                        tipo='INV-TR',
                        bodega_origen_id=bodega_origen.id,
                        bodega_destino_id=bodega_destino.id,
                        bodega_numero_origen=bodega_origen.codigo,
                        bodega_numero_destino=bodega_destino.codigo,
                        procesado=False,
                        detalle=''
                    )
                    tranferencia.save()

                    for item in self.request.data:
                        cantidad = Decimal(item['cantidad'])
                        if cantidad > 0:
                            tranferenci_dt_id = get_contador_sucdiv('INV_TRANSFERENCIAS_DT-ID-','{}{}'.format(sucursalid, divisionid[-1]))
                            producto = InvProductos.objects.get(pk=item['producto_id'])
                            tranferencia_detalle = InvTransferenciasDt(
                                id=tranferenci_dt_id,
                                transferencia_id=tranferencia.id,
                                producto_id=producto.id,
                                cantidad=cantidad,
                                empaque=item['empaque'],
                                costo=producto.costo_promedio,
                                factor=item['factor'],
                                total=round(cantidad * Decimal(item['factor']) * producto.costo_promedio,2),
                                sucursalid=sucursalid
                            )
                            tranferencia_detalle.save()

                    tranferencia.total = round(tranferencia.invtransferenciasdt_set.aggregate(costo_total=Coalesce(Sum('total'),0))['costo_total'],2)
                    tranferencia.save()
                    data['resp'] = True
                    return Response(data, status=200)

        except Exception as e:
            data['error'] = str(e)
        return Response(data, status=200)

class InvConsultaProductos(APIView):

    def get(self, request, *args, **kwargs):
        data = {'resp': False}
        try:
            accion = request.GET.get('accion', '')
            if accion == 'producto-codigo-barra':
                try:
                    codigo = self.request.GET.get('codigo')
                    tipo = self.request.GET.get('tipo','TR')
                    pe = InvProductosEmpaques.objects.filter(
                        Q(producto__anulado=False),
                        Q(codigo_barra=codigo) |
                        Q(producto__codigo=codigo),
                        Q(producto__clase='01')
                    ).exclude(codigo_barra='')[0]

                except:
                    raise Exception("No se encontro el producto ingresado..")

                try:
                    bodega_origen = InvBodegas.objects.get(anulado=False,pk=self.request.GET.get('bodega_id'))
                except:
                    raise Exception("No se encontro bodega de origen asociado al usuario..")

                try:
                    parametro = SisParametros.objects.get(codigo='INV-TRANSFERENCIA-CONTROLA-STOCK')
                    controla_stock = True if parametro.valor.upper() == 'SI' else False
                except:
                    controla_stock = True

                stock = Decimal('0.00')
                producto_stock = pe.producto.get_bodega_stock(bodega_origen.id,bodega_origen.sucursal)
                if producto_stock is not None:
                    stock = producto_stock['stock']

                if controla_stock and tipo == 'TR':
                    if stock <= 0:
                        raise Exception('El Producto {} se ecuentra Sin Stock'.format(pe.producto.codigo))

                data['producto'] = {
                    "producto_id": pe.producto_id,
                    "codigo": pe.codigo_barra.strip(),
                    "codigo_producto": pe.producto.codigo.strip(),
                    "empaque": pe.nombre.strip(),
                    "factor": round(pe.factor, 2),
                    "nombre": pe.producto.nombre.strip(),
                    "nombre_corto": pe.producto.nombre_corto.strip(),
                    "clase": pe.producto.clase,
                    "grupo_id": pe.producto.grupo_id.strip(),
                    "metodo": pe.producto.metodo.strip(),
                    "impuestoid": pe.producto.impuestoid.strip(),
                    "coniva": True if pe.producto.impuestoid.strip() else False,
                    "costo_compra": round(pe.producto.costo_compra, 4),
                    "costo_promedio": round(pe.producto.costo_promedio, 4),
                    "balanza": pe.producto.balanza,
                    "formato": pe.producto.descripcion,
                    "stock": round(stock,2) # round(stock/pe.producto.conversion,2)
                }
                data['resp'] = True
                return Response(data, status=200)

            elif accion == 'producto-empaques':

                empaques = InvProductosEmpaques.objects.filter(
                    producto_id=request.GET.get('producto_id'),
                    producto__anulado=False
                ).exclude(codigo_barra='').order_by('factor')

                lista_empaques = []
                for e in empaques:
                    lista_empaques.append({
                        'codigo': e.codigo.strip(),
                        'codigo_barra': e.codigo_barra.strip(),
                        'empaque': e.nombre.lower().strip(),
                        'factor': round(e.factor, 2),
                        'precio': e.precio,
                        'credito': e.credito,
                        'distribuidor': e.distribuidor,
                        'mayorista': e.mayorista
                    })

                data['empaques'] = lista_empaques
                return Response(data, status=200)

            elif accion == 'producto-bodegas':

                bodegas = InvBodegas.objects.filter(
                   anulado=False,
                   transferencia=True
                ).order_by('codigo')

                lista_bodegas = []
                for b in bodegas:
                    lista_bodegas.append({
                        'id': b.id,
                        'codigo': b.codigo,
                        'nombre': b.nombre,
                        'responsable': b.responsable,
                        'direccion': b.direccion,
                        'telefonos': b.telefonos,
                        'sucursal': b.sucursal,
                        'venta': b.venta
                    })

                data['bodegas'] = lista_bodegas
                return Response(data, status=200)

            elif accion == 'producto-buscar-nombre':

                bodegaid = request.GET.get('bodegaid', '')
                sucursalid = request.GET.get('sucursalid', '')
                s = '%{}%'.format(request.GET.get('criterio', ''))

                producto_empaques = InvProductosEmpaques.objects.filter(
                    producto__anulado=False
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
                return Response(data, status=200)

            elif accion == 'producto-autocomplete':
                s = '%{}%'.format(request.GET.get('criterio', ''))
                productos = InvProductos.objects.filter(
                    anulado=False,clase='01'
                ).extra(
                    where=["UPPER([INV_PRODUCTOS].[Nombre]) LIKE UPPER(%s)"], params=[s]
                ).order_by('codigo','nombre')[:30]

                lista_productos = []
                for p in productos:
                    lista_productos.append({
                        "producto_id": p.id,
                        "codigo_producto": p.codigo.strip(),
                        "nombre": '{} ({})'.format(p.nombre, p.descripcion)
                    })
                return Response({"productos": lista_productos}, status=200)

        except Exception as e:
            data['error'] = str(e)
        return Response(data, status=200)

class InvConsultaProductosClientes(APIView):
    def get(self, request, *args, **kwargs):
        data = {}
        try:
            accion = request.GET.get('accion', '')
            if accion == 'producto-codigo-barra':
                try:
                    codigo = self.request.GET.get('codigo')
                    pe = InvProductosEmpaques.objects.filter(
                        Q(producto__anulado=False),
                        Q(codigo_barra=codigo) |
                        Q(producto__codigo=codigo),
                        Q(producto__clase='01')
                    ).exclude(codigo_barra='')[0]
                except:
                    raise Exception("No se encontro el producto ingresado..")

                try:
                    bodega = InvBodegas.objects.get(anulado=False,codigo='01')
                except:
                    raise Exception("No se encontro bodega Almacen")

                tasa_impuesto = Decimal('0.00')
                if pe.producto.impuestoid.strip():
                    try:
                        parametro = SisParametros.objects.get(codigo='IMPUESTO-IVA')
                        tasa_impuesto = Decimal(parametro.valor.strip())
                    except:
                        pass

                empaques = InvProductosEmpaques.objects.filter(
                    producto_id=pe.producto_id,
                    producto__anulado=False
                ).exclude(Q(codigo_barra='')|Q(nombre__icontains='Neg')).order_by('factor')

                stock = Decimal('0.00')
                producto_stock = pe.producto.get_bodega_stock(bodega.id, bodega.sucursalid)
                if producto_stock is not None:
                    stock = producto_stock['stock']

                cantidad = Decimal(request.GET.get('cantidad', '1'))
                precios = self.empaque_precios(cantidad,pe.producto,pe,tasa_impuesto)

                lista_precios=[]
                for e in empaques:
                    lista_precios.append(self.empaque_precios(cantidad,e.producto,e,tasa_impuesto))

                data['producto'] = {
                    "producto_id": pe.producto_id,
                    "codigo": pe.codigo_barra.strip(),
                    "codigo_producto": pe.producto.codigo.strip(),
                    "empaque": pe.nombre.strip(),
                    "factor": round(pe.factor, 2),
                    "precio": precios['precio'],
                    "precio_pvp": precios['precio_pvp'],
                    "nombre": pe.producto.nombre.strip(),
                    "nombre_corto": pe.producto.nombre_corto.strip(),
                    "clase": pe.producto.clase,
                    "grupo": pe.producto.grupo.nombre.strip() if pe.producto.grupo is not None else 'NA',
                    "metodo": pe.producto.metodo.strip(),
                    "impuestoid": pe.producto.impuestoid.strip(),
                    "coniva": True if pe.producto.impuestoid.strip() else False,
                    "costo_compra": round(pe.producto.costo_compra, 4),
                    "costo_promedio": round(pe.producto.costo_promedio, 4),
                    "balanza": pe.producto.balanza,
                    "formato": pe.producto.descripcion,
                    "stock": round(stock/pe.producto.conversion,2),
                    "empaques": lista_precios
                }
                return Response(data, status=200)

        except Exception as e:
            data['error'] = str(e)
        return Response(data, status=200)

    def empaque_precios(self,cantidad,producto,empaque,tasa_impuesto):
        precio = Decimal('0.00')
        precio_pvp = Decimal('0.00')

        if (cantidad * empaque.factor) < 1:
            rangos = InvProductosPrecios.objects.filter(
                producto_id=producto.id,
                rango1__lte=empaque.factor,
                rango2__gte=empaque.factor
            ).order_by('-rango1')
        else:
            parte_decimal = empaque.factor % 1
            if parte_decimal > 0:
                rangos = InvProductosPrecios.objects.filter(
                    producto_id=producto.id,
                    rango1__lte=(empaque.factor * cantidad),
                    rango2__gte=(empaque.factor * cantidad)
                ).order_by('-rango1')
            else:
                rangos = InvProductosPrecios.objects.filter(
                    producto_id=producto.id,
                    rango1__lte=int(empaque.factor * cantidad),
                    rango2__gte=int(empaque.factor * cantidad)
                ).order_by('-rango1')

        if rangos.exists():
            rango = rangos[0]
            precio = round(rango.precio * empaque.factor, 4)
            precio_pvp = precio
            if producto.impuestoid.strip():
                precio_pvp = round(precio * (1 + (tasa_impuesto / 100)), 4)

        precio_pvp = round(precio_pvp * cantidad, 2)
        return {'empaque': empaque.nombre.strip(),'precio': precio, 'precio_pvp': precio_pvp, 'rango': rango.rango1, 'precio_und': round(precio_pvp/empaque.factor,2)}

class InvTomaFisico(APIView):
    def post(self, request,accion,pk, *args, **kwargs):
        data = {}
        try:
            if accion == 'guardar-pendientes':
                with transaction.atomic():
                    try:
                        fisico = InvFisico.objects.get(anulado=False,pk=pk)
                    except:
                        raise Exception("No se econtro toma fisico ID")

                    sucursalid = fisico.sucursalid
                    divisionid = fisico.division_id

                    for item in self.request.data:
                        cantidad = Decimal(item['cantidad'])
                        if cantidad > 0:
                            producto = InvProductos.objects.get(pk=item['producto_id'])
                            stock = Decimal('0.00')
                            producto_stock = producto.get_bodega_stock_sistema(fisico.bodega_id,sucursalid)
                            if producto_stock is not None:
                                stock = producto_stock['stock']
                            else:
                                with connection.cursor() as cursor:
                                    cursor.execute(
                                        "{CALL Inv_ProductoBodega_Stock_Insert(%s,%s,%s)}", (
                                           producto.id,
                                           fisico.bodega_id,
                                           Decimal("0.00")
                                        ))
                                stock = 0

                            fisico_producto_id = get_contador_sucdiv('INV_TOMA_FISICO_DT-','{}{}'.format(sucursalid, divisionid[-1]))

                            fisico_producto = InvFisicoProductos(
                                id=fisico_producto_id,
                                fisico_id=fisico.id,
                                producto_id=producto.id,
                                stock=stock,
                                costo=producto.costo_promedio,
                                cantidad=cantidad,
                                empaque=item['empaque'],
                                factor=Decimal(item['factor']),
                                unidades=round(cantidad * Decimal(item['factor']), 2),
                                total_unidades=round(cantidad * Decimal(item['factor']) * producto.costo_promedio, 2),
                                sucursalid=fisico.sucursalid
                            )
                            fisico_producto.save()


                    fisico_productos = fisico.invfisicoproductos_set.filter(anulado=False, procesado=False) \
                        .values('producto_id') \
                        .annotate(unds=Coalesce(Sum(F('cantidad') * F('factor')), 0)) \
                        .order_by('producto_id')

                    for item in fisico_productos:
                        producto = InvProductos.objects.get(pk=item['producto_id'])
                        stock = producto.get_bodega_stock_sistema(fisico.bodega_id,sucursalid)['stock']
                        fisico_stock = round(item['unds'], 2)

                        if round(stock - fisico_stock, 2) == Decimal("0.00"):
                            try:
                                fisico.invfisicoproductos_set.filter(
                                    anulado=False,
                                    producto_id=item['producto_id']
                                ).update(
                                    procesado=True
                                )
                            except:
                                pass
                    data['resp'] = True
                    return Response(data, status=200)
        except Exception as e:
            data['error'] = str(e)
        return Response(data, status=200)

    def get(self, request, *args, **kwargs):
        data = {}
        try:
            accion = request.GET.get('accion', '')
            if accion == 'inv-toma-fisico':
                fisicos = InvFisico.objects.filter(
                    anulado=False,
                    procesado=False
                ).order_by('creadodate')

                lista_fisicos = []
                for f in fisicos:
                    lista_fisicos.append({
                        'id': f.id,
                        'numero': f.numero,
                        'fecha': f.fecha.strftime("%Y-%m-%d"),
                        'detalle': f.detalle,
                        'bodega' : {"id":f.bodega.id,"nombre": f.bodega.nombre},
                        'sucursalid': f.sucursalid,
                        'divisionid': f.division.id
                    })
                data['toma_fisicos'] = lista_fisicos
                return Response(data, status=200)

        except Exception as e:
            data['error'] = str(e)
        return Response(data, status=200)

