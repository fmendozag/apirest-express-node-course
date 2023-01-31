from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.shortcuts import redirect
from django.utils.datetime_safe import datetime
from easy_pdf.rendering import render_to_pdf_response
import datetime

from inventario.models import InvFisico, InvConteoDt, InvProductos
from sistema.constantes import NOMBRE_SISTEMA, LOGO_INFORME_CABECERA, NOMBRE_INSTITUCION, INSTITUCION_CIUDAD, \
    INSTITUCION_DIRECCION, INSTITUCION_DIRECCION2, INSTITUCION_TELEFONO

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def tomaFisicoConteoDetImprimir(request,pid):
    if request.method == 'GET':
        data = {}
        try:
            try:
                toma_fisico = InvFisico.objects.get(pk=pid, anulado=False)
            except:
                raise Exception("No se econtro la toma fisica Id.")

            data['title'] = 'Documento orden de pedido'
            data['sistema'] = NOMBRE_SISTEMA
            data['logo_cabecera'] = LOGO_INFORME_CABECERA
            data['belbry'] = NOMBRE_INSTITUCION
            data['ciudad'] = INSTITUCION_CIUDAD
            data['direccion'] = INSTITUCION_DIRECCION
            data['direccion2'] = INSTITUCION_DIRECCION2
            data['telefono'] = INSTITUCION_TELEFONO
            data['hoy'] = datetime.datetime.now()
            data['toma_fisico'] = toma_fisico
            data['usuario'] = request.user.username
            data['titulo'] = 'Comprobante de Conteo Detalle'

            productos = []

            conteo_detalle = InvConteoDt.objects.filter(anulado=False,conteo__toma_fisica=toma_fisico).order_by('producto__codigo')

            for item in conteo_detalle:
                stock_sistema = item.producto.get_bodega_stock_sistema(toma_fisico.bodega.id, toma_fisico.sucursalid)['stock']
                productos.append({
                    'codigo': item.producto.codigo,
                    'producto': item.producto,
                    'empaque': "Und",
                    'factor': Decimal(1.00),
                    'stock_ant': item.stock,
                    'diferencia_ant': round(item.stock - item.cantidad, 2),
                    'fisico_stock': item.cantidad,
                    'stock_sistema': stock_sistema,
                    'diferencia_sistema': round(stock_sistema - item.cantidad, 2),
                    'procesado': item.procesado,
                    'transferencia': item.transferencia,
                    'ajuste': item.ajuste,
                    'ingreso': item.ingreso,
                    'egreso': item.egreso,
                })

            data['productos_detalle'] = productos

            return render_to_pdf_response(request,"informe/toma-fisica/inv_informe_toma_fisica_conteo_detalle.html", data)
        except:
            raise

    return redirect('/')

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def toma_fisica_inv_documento(request,pid):
    if request.method == 'GET':
        data = {}
        try:
            try:
                toma_fisico = InvFisico.objects.get(pk=pid, anulado=False)
            except:
                raise Exception("No se econtro la toma fisica Id.")

            data['title'] = 'Documento Toma Física'
            data['sistema'] = NOMBRE_SISTEMA
            data['logo_cabecera'] = LOGO_INFORME_CABECERA
            data['belbry'] = NOMBRE_INSTITUCION
            data['ciudad'] = INSTITUCION_CIUDAD
            data['direccion'] = INSTITUCION_DIRECCION
            data['direccion2'] = INSTITUCION_DIRECCION2
            data['telefono'] = INSTITUCION_TELEFONO
            data['hoy'] = datetime.datetime.now()
            data['toma_fisico'] = toma_fisico
            data['usuario'] = request.user.username
            data['titulo'] = 'Comprobante de Toma Física'

            return render_to_pdf_response(request, "informe/toma-fisica/inv_informe_toma_fisica_detalle.html", data)

        except:
            raise
    return redirect('/')

@login_required(redirect_field_name='ret', login_url='/seguridad/login/')
def informe_toma_fisica_detalle_agrupado(request,pid):
    if request.method == 'GET':
        data = {}
        try:
            try:
                toma_fisico = InvFisico.objects.get(pk=pid, anulado=False)
            except:
                raise Exception("No se econtro la toma fisica Id.")

            if toma_fisico.bodega is None:
                raise Exception("No se encontro bodega..")

            fisico_productos = toma_fisico.invfisicoproductos_set.filter(anulado=False) \
                .values('producto_id') \
                .annotate(unds=Coalesce(Sum(F('cantidad') * F('factor')), 0)) \
                .order_by('producto_id')

            productos = []
            bodegaid = toma_fisico.bodega_id
            sucursalid = toma_fisico.sucursalid

            for item in fisico_productos:
                producto = InvProductos.objects.get(pk=item['producto_id'])
                stock = producto.get_bodega_stock_sistema(bodegaid, sucursalid)['stock']
                fisico_stock = round(item['unds'], 2)
                stock_conversion = (stock / producto.conversion)
                fisico_conversion = (fisico_stock / producto.conversion)

                productos.append({
                    'codigo': producto.codigo,
                    'empaque': "Und.",
                    'factor': Decimal(1.00),
                    'producto': producto,
                    'fisico_stock': fisico_stock,
                    'fisico_cajas': int(fisico_conversion),
                    'fisico_unidades': round((fisico_conversion % 1) * producto.conversion, 2),
                    'stock': stock,
                    'conversion': round(producto.conversion, 2),
                    'stock_conversion': round(stock_conversion, 2),
                    'cajas': int(stock_conversion),
                    'unidades': round((stock_conversion % 1) * producto.conversion, 2),
                    'diferencia': round(stock - fisico_stock, 2),
                })

            data['productos_detalle'] = productos

            data['toma_fisico'] = toma_fisico


            return render_to_pdf_response(request, "informe/toma-fisica/inv_informe_toma_fisica_detalle_agrupado.html", data)

        except:
            raise
    return redirect('/')

