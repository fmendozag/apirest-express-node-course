import json
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic.base import View
from venta.models import VenFacturas

class PosPuntoVentaImprimir(LoginRequiredMixin, View):
    login_url = '/seguridad/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        data = {}
        try:
            djson = json.loads(request.GET['data_json'])
            tipo = djson['tipo']
            documentos = [d['factura_id'] for d in djson['documentos']]
            data['ventas'] = VenFacturas.objects.filter(anulado=False,pk__in=documentos)
            if tipo == 'FA':
                return render(request, 'pos/imprimir/pos_factura_venta.html', data)
            else:
                return render(request, 'pos/imprimir/pos_nota_venta.html', data)
        except Exception as e:
            messages.add_message(request, 40, str(e))
        return redirect('/')
