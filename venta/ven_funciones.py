from django.db import connection
from cliente.models import CliClientesDeudas
from contabilidad.models import AccAsientos


def fn_actualizar_venta(documento):
    cursor = connection.cursor()
    cursor.execute("UPDATE INV_PRODUCTOS_CARDEX SET Fecha = %s WHERE DocumentoID= %s",
                   [documento.fecha.date(), documento.id])
    asiento = AccAsientos.objects.get(pk=documento.asientoid, documentoid=documento.id)
    asiento.fecha = documento.fecha.date()
    asiento.save()

    cliente_deuda = CliClientesDeudas.objects.get(cliente_id=documento.cliente_id, documentoid=documento.id)
    cliente_deuda.fecha = documento.fecha.date()
    cliente_deuda.vendedorid = documento.vendedorid
    cliente_deuda.save()
