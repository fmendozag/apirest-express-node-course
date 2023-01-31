from crum import get_current_user
from django.db import models
from django.utils.timezone import now

from sistema.constantes import ESTADO_ORDEN_PEDIDO

class VenOrdenPedidos(models.Model):
    cliente = models.ForeignKey('cliente.CliClientes', on_delete=models.PROTECT, max_length=10, blank=True, null=True,default='')
    detalle = models.CharField(max_length=100, blank=True, null=True, default='')
    ruc = models.CharField(max_length=13, blank=True, null=True, default='')
    vendedor = models.ForeignKey('empleado.EmpEmpleados', on_delete=models.PROTECT, max_length=10, blank=True,null=True, default='')
    empleadoid = models.CharField(max_length=10, blank=True, null=True, default='')
    terminoid = models.CharField(max_length=10, blank=True, null=True, default='')
    division = models.ForeignKey('sistema.SisDivisiones',on_delete=models.PROTECT,max_length=10, blank=True, null=True,default='')
    caja = models.ForeignKey('banco.BanBancos',on_delete=models.PROTECT, max_length=10, blank=True, null=True,default='')
    bodega = models.ForeignKey('inventario.InvBodegas', on_delete=models.PROTECT, max_length=10, blank=True, null=True,default='')
    contado = models.BooleanField(default=False)
    numero = models.CharField(max_length=10, blank=True, null=True, editable=False)
    fecha = models.DateTimeField(default=now)
    entregado = models.DateTimeField(default=now, blank=True, null=True)
    tipo = models.CharField(max_length=10, blank=True, null=True, default='PED-VEN')
    divisaid = models.CharField(max_length=10, blank=True, null=True, default='')
    cambio = models.DecimalField(max_digits=12, decimal_places=6,blank=True, null=True, default=1)
    subtotal = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    descuento = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    impuesto = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    total = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    nota = models.CharField(max_length=1024, blank=True, null=True, default='')
    estado = models.CharField(max_length=1,choices=ESTADO_ORDEN_PEDIDO, blank=True, null=True, default='1')
    procesado = models.BooleanField(default=False)
    negado = models.BooleanField(default=False)
    aprobado = models.BooleanField(default=False)
    aprobadonota = models.CharField(max_length=1024, blank=True, null=True, editable=False)
    aprobadopor = models.CharField(max_length=15, blank=True, null=True, editable=False)
    aprobadodate = models.DateTimeField(blank=True, null=True, editable=False)
    anulado = models.BooleanField(default=False)
    creadopor = models.CharField(max_length=15, blank=True, null=True, editable=False)
    creadodate = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)
    anuladonota = models.CharField(max_length=1024, blank=True, null=True, editable=False)
    anuladopor = models.CharField(max_length=15, blank=True, null=True, editable=False)
    anuladodate = models.DateTimeField(blank=True, null=True, editable=False)
    editadopor = models.CharField(max_length=15, blank=True, null=True, editable=False)
    editadodate = models.DateTimeField(auto_now=True, blank=True, null=True, editable=False)
    sucursalid = models.CharField(max_length=2, blank=True, null=True, editable=False)
    pcid = models.CharField(max_length=100, blank=True, null=True, editable=False, default='')
    verificadorid = models.CharField(max_length=10, blank=True, null=True, default='')
    recaudadorid = models.CharField(max_length=10, blank=True, null=True, default='')
    entregadorid = models.CharField(max_length=10, blank=True, null=True, default='')
    dia_cobro = models.IntegerField(blank=True, null=True, default=0)
    zona = models.ForeignKey('sistema.SisZonas', on_delete=models.PROTECT, max_length=10, blank=True, null=True,default='')
    numcartilla = models.CharField(max_length=15, blank=True, null=True, default='')
    subtotal_cero = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True, default=0)
    subtotal_iva = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True, default=0)
    descuento_cero = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True, default=0)
    descuento_iva = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True, default=0)
    total_comision = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True, default=0)
    costo_total = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True, default=0)
    forma_pago = models.CharField(max_length=3, blank=True, null=True,default='')
    dias_credito = models.IntegerField(blank=True, null=True, default=0)
    nocontrola_stock = models.BooleanField(blank=True, null=True, default=False)
    vence = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.detalle)

    class Meta:
        verbose_name = 'Orden de pedido'
        verbose_name_plural = 'Ordenes de pedidos'
        ordering = ['-creadodate']

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        add = False
        try:
            user = get_current_user()
            if self._state.adding:
                add = True
                self.creadopor = user.username
            else:
                self.editadopor = user.username
        except:
            pass
        super(VenOrdenPedidos, self).save(force_insert, force_update, using)
        if add:
            try:
                self.numero = str(self.id).zfill(10)
            except:
                pass
            super(VenOrdenPedidos, self).save()

class VenOrdenPedidosDetalle(models.Model):
    orden_pedido = models.ForeignKey(VenOrdenPedidos, on_delete=models.PROTECT)
    producto = models.ForeignKey('inventario.InvProductos',on_delete=models.PROTECT,max_length=10, blank=True, null=True,default='')
    bodega = models.ForeignKey('inventario.InvBodegas', on_delete=models.PROTECT,max_length=10, blank=True, null=True,default='')
    codigo = models.CharField(max_length=20,blank=True, null=True,default='')

    cantidad = models.DecimalField(max_digits=11, decimal_places=2,default=0)
    sugerido = models.DecimalField(max_digits=11, decimal_places=2,default=0)

    facturado = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True,default=0)
    egresado = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True,default=0)
    precio = models.DecimalField(max_digits=19, decimal_places=4,default=0)
    precio_display = models.DecimalField(max_digits=19, decimal_places=4,default=0)
    precio_factor = models.DecimalField(max_digits=19, decimal_places=4,default=0)
    precio_final = models.DecimalField(max_digits=19, decimal_places=4,default=0)

    costo = models.DecimalField(max_digits=19, decimal_places=4,default=0)
    ctacosto_id = models.CharField(max_length=10, blank=True, null=True,default='')
    ctadescuento_id = models.CharField(max_length=10, blank=True, null=True,default='')
    ctadevolucion_id = models.CharField(max_length=10, blank=True, null=True,default='')
    ctaimpuestoid = models.CharField(max_length=10, blank=True, null=True,default='')
    ctamayor_id = models.CharField(max_length=10, blank=True, null=True,default='')
    ctaventa_id = models.CharField(max_length=10, blank=True, null=True,default='')

    subtotal = models.DecimalField(max_digits=19, decimal_places=4,default=0)
    tasa_descuento = models.DecimalField(max_digits=5, decimal_places=2, blank=True,null=True, default=0)
    descuento = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True,default=0)
    tasa_impuesto = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,default=0)
    impuesto = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True,default=0)
    impuestoid = models.CharField(max_length=10, blank=True, null=True,default='')
    total = models.DecimalField(max_digits=19, decimal_places=4,default=0)
    clase = models.CharField(max_length=2, blank=True, null=True)

    empaque = models.CharField(max_length=40, blank=True, null=True)
    embarque = models.BooleanField(default=False)
    coniva = models.BooleanField(default=False)
    factor = models.DecimalField(max_digits=6, decimal_places=2,default=1)
    formato = models.CharField(max_length=30,blank=True, null=True,default='')
    aprobado = models.BooleanField(default=False)
    creadopor = models.CharField(max_length=15, blank=True, null=True,editable=False)
    creadodate = models.DateTimeField(auto_now_add=True,blank=True, null=True,editable=False)
    editadopor = models.CharField(max_length=15, blank=True, null=True,editable=False)
    editadodate = models.DateTimeField(auto_now=True,blank=True, null=True,editable=False)
    sucursalid = models.CharField(max_length=2, blank=True, null=True,editable=False)
    pcid = models.CharField(max_length=50, blank=True, null=True, editable=False,default='')
    valor_comision = models.DecimalField(max_digits=19, decimal_places=4, blank=True,null=True, default=0)

    comision_contado =models.DecimalField(max_digits=19, decimal_places=2, blank=True,null=True, default=0)
    comision_credito =models.DecimalField(max_digits=19, decimal_places=2, blank=True,null=True, default=0)

    tasa_descuento_contado =models.DecimalField(max_digits=19, decimal_places=2, blank=True,null=True, default=0)
    tasa_descuento_credito =models.DecimalField(max_digits=19, decimal_places=2, blank=True,null=True, default=0)

    def __str__(self):
        return '{}'.format(self.producto.nombre)

    class Meta:
        verbose_name = 'Orden de pedido detalle'
        verbose_name_plural = 'Orden de pedidos detalles'
        ordering = ['-creadodate']

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
            else:
                self.editadopor = user.username
        except:
            pass
        super(VenOrdenPedidosDetalle, self).save(force_insert, force_update, using)
