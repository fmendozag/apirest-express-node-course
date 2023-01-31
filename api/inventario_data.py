from decimal import Decimal
from rest_framework.response import Response
from rest_framework.views import APIView
from inventario.models import InvProductosEmpaques, InvProductos
from sistema.models import SisParametros
class InvProductosMovilView(APIView):
    def get(self, request, *args, **kwargs):
        data = {'resp': False}
        try:
            accion = request.GET.get('accion', '')
            if accion == 'inv-productos':

                minimo = int(request.GET.get('minimo'))
                maximo = int(request.GET.get('maximo'))

                productos = InvProductos.objects.filter(
                    anulado=False,
                    #ubicacionid=UBICACION_ID,
                    vendible=True,
                ).order_by('id')[minimo:maximo]

                tasa_impuesto = Decimal('0.00')
                try:
                    tasa_impuesto = SisParametros.objects.get(codigo='IMPUESTO-IVA').valor.strip()
                except:
                    pass
                try:
                    bodega = self.request.user.segusuarioparametro.caja.bodega
                except:
                    raise Exception('No se encontro bodega asociado al usuario')

                lista_productos = []
                for p in productos:
                    empaques = []
                    for pe in InvProductosEmpaques.objects.filter(
                        producto_id=p.id).exclude(codigo_barra='').exclude(codigo='N').order_by('factor'):
                        empaques.append({
                            'producto_id': p.id,
                            'codigo': pe.codigo.strip(),
                            'codigo_barra': pe.codigo_barra.strip(),
                            'empaque': pe.nombre.strip(),
                            'factor': pe.factor,
                            'precio': pe.precio,
                            'credito': pe.credito,
                            'distribuidor': pe.distribuidor,
                            'mayorista': pe.mayorista,
                        })
                        stock = Decimal('0.00')
                        producto_stock = pe.producto.get_bodega_stock(bodega.id,bodega.sucursal)
                        if producto_stock is not None:
                            stock = producto_stock['stock']

                    lista_productos.append({
                        'producto_id': p.id,
                        'codigo': p.codigo.strip() if p.codigo is not None else '',
                        'nombre': p.nombre.strip() if p.nombre is not None else '',
                        'nombre_corto': p.nombre_corto.strip() if p.nombre_corto is not None else '',
                        'formato': p.descripcion.strip() if p.descripcion is not None else '',
                        'grupo': p.grupo.nombre.strip() if p.grupo is not None else '',
                        'marca': p.marca.strip() if p.marca is not None else '',
                        'impuestoid': p.impuestoid.strip() if p.impuestoid is not None else '',
                        'tasa_impuesto': tasa_impuesto if p.impuestoid.strip() else Decimal('0.00'),
                        'empaque': p.empaque.strip() if p.empaque is not None else '',
                        'costo_compra': p.costo_compra,
                        'precio': p.precio4,
                        'conversion': p.conversion,
                        'balanza': p.balanza,
                        'codigo_barra_unidad': p.codigo_barra1.strip() if p.codigo_barra1 is not None else '',
                        'codigo_barra_caja': p.codigo_barra2.strip() if p.codigo_barra2 is not None else '',
                        'ptg_descuento': p.ptg_descuento,
                        'stock': round(stock,2),
                        'bodega_id': bodega.id if bodega is not None else '',
                        'empaques': empaques
                    })

                data['productos'] = lista_productos
                data['resp'] = True
                return Response(data, status=200)

            elif accion == 'inv-productos-items':
                items = InvProductos.objects.filter(
                    anulado=False,
                    vendible=True,
                ).count()
                data['resp'] = True
                data['items'] = items
                return Response(data, status=200)

        except Exception as e:
            data['error'] = str(e)
        return Response(data, status=200)
