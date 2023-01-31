from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic.base import View
from acreedor.models import AcrAcreedores
from inventario.models import InvBodegas, InvGrupos, InvPdBodegaStock, InvProductosPrecios
from sistema.funciones import addUserData

class InvPlacaPrecios(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        data = {'resp': False, 'error': ''}
        try:
            accion = request.POST.get('accion',None)
            if accion == 'inv-productos-stock-precios':
                producto_id = self.request.POST.get('producto_id',None)
                if producto_id is None or producto_id == '':
                    criterio = {
                        'bodega_id':self.request.POST.get('bodega_id'),
                        'producto__proveedor_id':self.request.POST.get('proveedor_id'),
                        'producto__grupo_id':self.request.POST.get('grupo_id')
                    }
                else:
                    criterio = {
                        'producto_id': producto_id
                    }
                def queries(filters):
                    return [Q(**{k: v}) for k, v in filters.items() if v]

                productos_stock = InvPdBodegaStock.objects.filter(
                    Q(stock__gt=0),
                    *queries(criterio)
                ).order_by('producto__nombre')


                lista_productos=[]
                for ps in productos_stock:

                    unidad = Decimal('1.00')
                    docena = Decimal('12.00')

                    stock_conversion = ps.stock / ps.producto.conversion
                    producto_precios = InvProductosPrecios.objects.filter(producto_id=ps.producto.id)
                    rango_unidad = producto_precios.filter(rango1__lte=unidad,rango2__gte=unidad).order_by('rango1').first()
                    rango_docena = producto_precios.filter(rango1__lte=docena,rango2__gte=docena).order_by('rango1').first()
                    rango_caja = producto_precios.filter(rango1__lte=int(ps.producto.conversion),rango2__gte=int(ps.producto.conversion)).order_by('rango1').first()
                    con_iva = True if ps.producto.impuestoid.strip() else False

                    pvp_unidad = rango_unidad.precio_final if rango_unidad is not None else 0
                    pvp_docena = rango_docena.precio_final if rango_docena is not None else 0
                    pvp_caja = (round(rango_caja.precio_final,2) * ps.producto.conversion) if rango_caja is not None else 0

                    lista_productos.append(
                        {
                            'producto_id': ps.producto.id,
                            'codigo': ps.producto.codigo,
                            'nombre': ps.producto.nombre,
                            'fomato': ps.producto.descripcion,
                            'cajas': int(stock_conversion),
                            'unidades': round((stock_conversion % 1) * ps.producto.conversion,2),
                            'stock': ps.stock,
                            'pvp_unidad': round(pvp_unidad,2),
                            'pvp_docena': round(pvp_docena,2),
                            'pvp_caja': round(pvp_caja,2),
                            'con_iva': con_iva
                        }
                    )
                data['productos'] = lista_productos
                data['resp'] = True
                return JsonResponse(data, status=200)
        except Exception as e:
            data['error'] = 'error: ' + str(e)
        return JsonResponse(data, status=200)

    def get(self, request, *args, **kwargs):
        data = {"procesar":False}
        addUserData(request, data)
        try:
            data['bodegas'] = InvBodegas.objects.filter(anulado=False)
            data['proveedores'] = AcrAcreedores.objects.filter(anulado=False).order_by('nombre')
            data['grupos'] = InvGrupos.objects.filter(anulado=False).order_by('nombre')
            return render(request,'inventario/inv_placa_precios.html',data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')
