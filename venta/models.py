from crum import get_current_user
from django.db import models
from django.utils.timezone import now
from cliente.models import CliClientes
from empleado.models import EmpEmpleados
from sistema.constantes import TIPO_DOCUMENTO_FACTURA, ESTADO_COMISION, TIPO_DOCUMENTO_COMISION, TIPO_MODELO
from sistema.models import SisParametros

class VenFacturas(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    ordenid = models.CharField(db_column='OrdenID', max_length=10, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    cliente = models.ForeignKey('cliente.CliClientes', models.DO_NOTHING,db_column='ClienteID', max_length=10)  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=100, blank=True, null=True,default='')  # Field name made lowercase.
    ruc = models.CharField(db_column='Ruc', max_length=13, blank=True, null=True,default='')  # Field name made lowercase.
    asientoid = models.CharField(db_column='AsientoID', max_length=10,default='',editable=False)  # Field name made lowercase.
    vendedorid = models.CharField(db_column='VendedorID', max_length=10,default='')  # Field name made lowercase.
    empleadoid = models.CharField(db_column='EmpleadoID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    terminoid = models.CharField(db_column='TérminoID', max_length=10,default='')  # Field name made lowercase.
    ingresoid = models.CharField(db_column='IngresoID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    division = models.ForeignKey('sistema.SisDivisiones', models.DO_NOTHING,db_column='DivisiónID', blank=True, null=True)  # Field name made lowercase.
    caja = models.ForeignKey('banco.BanBancos', models.DO_NOTHING,db_column='CajaID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    secuencia = models.CharField(db_column='Secuencia', max_length=20, blank=True, null=True,default='')  # Field name made lowercase.
    bodega = models.ForeignKey('inventario.InvBodegas', models.DO_NOTHING,db_column='BodegaID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    contado = models.BooleanField(db_column='Contado',default=False)  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha')  # Field name made lowercase.
    entregado = models.DateTimeField(db_column='Entregado', blank=True, null=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10,choices=TIPO_DOCUMENTO_FACTURA)  # Field name made lowercase.
    divisaid = models.CharField(db_column='DivisaID', max_length=10)  # Field name made lowercase.
    cambio = models.DecimalField(db_column='Cambio', max_digits=12, decimal_places=6,default=1)  # Field name made lowercase.
    subtotal = models.DecimalField(db_column='Subtotal', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    descuento = models.DecimalField(db_column='Descuento', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    impuesto = models.DecimalField(db_column='Impuesto', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    total = models.DecimalField(db_column='Total', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    transporte = models.CharField(db_column='Transporte', max_length=30,default='')  # Field name made lowercase.
    efectivo = models.DecimalField(db_column='Efectivo', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    cheque = models.DecimalField(db_column='Cheque', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    tarjeta = models.DecimalField(db_column='Tarjeta', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    credito = models.DecimalField(db_column='Crédito', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    banco = models.CharField(db_column='Banco', max_length=50, blank=True, null=True,default='')  # Field name made lowercase.
    fecha_cheque = models.DateTimeField(db_column='Fecha_Cheque', blank=True, null=True)  # Field name made lowercase.
    nocuenta = models.CharField(db_column='NoCuenta', max_length=50, blank=True, null=True,default='')  # Field name made lowercase.
    nocheque = models.CharField(db_column='NoCheque', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    nombre_tarjeta = models.CharField(db_column='Nombre_Tarjeta', max_length=50, blank=True, null=True,default='')  # Field name made lowercase.
    vence = models.DateTimeField(db_column='Vence', blank=True, null=True)  # Field name made lowercase.
    notarjeta = models.CharField(db_column='NoTarjeta', max_length=20, blank=True, null=True,default='')  # Field name made lowercase.
    autorizacion = models.CharField(db_column='Autorización', max_length=100, blank=True, null=True,default='')  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True,default='')  # Field name made lowercase.
    nota2 = models.CharField(db_column='Nota2', max_length=1024, blank=True, null=True,default='')  # Field name made lowercase.
    croquis = models.BooleanField(db_column='Croquis',default=False)  # Field name made lowercase.
    cerrada = models.BooleanField(db_column='Cerrada',default=False)  # Field name made lowercase.
    remunerada = models.BooleanField(db_column='Remunerada',default=False)  # Field name made lowercase.
    remunerar = models.BooleanField(db_column='Remunerar',default=False)  # Field name made lowercase.
    transferido = models.BooleanField(db_column='Transferido',default=False)  # Field name made lowercase.
    comision = models.DecimalField(db_column='Comisión', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    comision_nota = models.CharField(db_column='Comisión_Nota', max_length=1024, blank=True, null=True,default='')  # Field name made lowercase.
    numero_guia = models.CharField(db_column='Número_Guía', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    numero_oc = models.CharField(db_column='Número_OC', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    fecha_oc = models.DateTimeField(db_column='Fecha_OC', blank=True, null=True)  # Field name made lowercase.
    fact_preimpresa = models.CharField(db_column='Fact_Preimpresa', max_length=20, blank=True, null=True,default='')  # Field name made lowercase.
    rolid = models.CharField(db_column='RolID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    holgura = models.DecimalField(db_column='Holgura', max_digits=2, decimal_places=0, blank=True, null=True,default=2)  # Field name made lowercase.
    tipo_factura = models.CharField(db_column='TipoFactura', max_length=1, blank=True, null=True,default='')  # Field name made lowercase.
    despachado = models.BooleanField(db_column='Despachado',default=False)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(auto_now_add=True,db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladonota = models.CharField(db_column='AnuladoNota', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladodate = models.DateTimeField(db_column='AnuladoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(auto_now=True,db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    retenido = models.BooleanField(db_column='Retenido',default=False)  # Field name made lowercase.
    procesado_sri = models.BooleanField(db_column='Procesado_SRI', blank=True, null=True,default=False)  # Field name made lowercase.
    nocontrola_stock = models.BooleanField(db_column='NoControlaStock', blank=True, null=True,default=False)  # Field name made lowercase.
    clase_cliente = models.CharField(db_column='ClaseCliente', max_length=2, blank=True, null=True,default='')  # Field name made lowercase.
    tipo_llamadaid = models.CharField(db_column='TipoLlamadaID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    tipo_visitaid = models.CharField(db_column='TipoVisitaID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    cupones = models.DecimalField(db_column='Cupones', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    reimpreso = models.BooleanField(db_column='Reimpreso', default=False)  # Field name made lowercase.
    forma_pago = models.CharField(db_column='FormaPago', max_length=3, blank=True, null=True)  # Field name made lowercase.
    dias_credito = models.IntegerField(db_column='DiasCredito', blank=True, null=True,default=0)  # Field name made lowercase.
    ptg_iva = models.DecimalField(db_column='PtgIVA', max_digits=6, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fecha_autorizacion = models.CharField(db_column='FechaAutorización', max_length=30, blank=True, null=True)  # Field name made lowercase.
    pago_cliente = models.DecimalField(db_column='PagoCliente', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    vuelto_cliente = models.DecimalField(db_column='VueltoCliente', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    reciboid = models.CharField(db_column='ReciboID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    verificadorid = models.CharField(db_column='VerificadorID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    recaudadorid = models.CharField(db_column='RecaudadorID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    entregadorid = models.CharField(db_column='EntregadorID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    dia_cobro = models.IntegerField(db_column='DiaCobro', blank=True, null=True,default=0)  # Field name made lowercase.
    zona = models.ForeignKey('sistema.SisZonas', models.DO_NOTHING,db_column='ZonaID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    pagada = models.BooleanField(db_column='Pagada', blank=True, null=True,default=False)  # Field name made lowercase.
    pagada_fecha = models.DateTimeField(db_column='PagadaFecha', blank=True, null=True)  # Field name made lowercase.
    numcartilla = models.CharField(db_column='NumCartilla', max_length=15, blank=True, null=True)  # Field name made lowercase.
    saldo_cartilla = models.DecimalField(db_column='SaldoCartilla', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    archivo_sri = models.BooleanField(db_column='ArchivoSRI',default=False)  # Field name made lowercase.
    subtotal_cero = models.DecimalField(db_column='SubTotalCero', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    subtotal_iva = models.DecimalField(db_column='SubTotalIVA', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    descuento_cero = models.DecimalField(db_column='DescuentoCero', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    descuento_iva = models.DecimalField(db_column='DescuentoIVA', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    total_rentabilidad = models.DecimalField(db_column='TotalRentabilidad', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    total_comision = models.DecimalField(db_column='TotalComision', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    tipo_modelo = models.CharField(db_column='TipoModelo',choices=TIPO_MODELO, max_length=10, blank=True,null=True,default='')  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.detalle)

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        managed = False
        db_table = 'VEN_FACTURAS'

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
            else:
                self.editadopor = user.username
        except:
            pass
        super(VenFacturas, self).save(force_insert, force_update, using)

    def get_vendedor(self):
        try:
            return EmpEmpleados.objects.get(anulado=False,pk=self.vendedorid)
        except:
            pass
        return None

    def get_forma_pago(self):
        if self.forma_pago == 'EFE':
            return 'EFECTIVO'
        elif self.forma_pago == 'CRE':
            return 'CREDITO'
        elif self.forma_pago == 'CHE':
            return 'CHEQUE '
        elif self.forma_pago == 'TAR':
            return 'TARJETA'
        return ''

    def get_pv_venta_detalle(self):
        return self.venfacturasdetalle_set.all()

    def get_pv_count_items(self):
        return self.venfacturasdetalle_set.count()

    def get_pv_restante_items(self):
        try:
            items_maximo = int(SisParametros.objects.get(codigo='POS-MAX-ITEMS').valor)
        except:
            items_maximo = 24
        return range(items_maximo - self.venfacturasdetalle_set.count())

    def get_pv_cliente_ruc(self):
        return '{:>13}'.format(self.cliente.ruc)

    def get_pv_subtotal_nv_str(self):
        subtotal = '{:>9}'.format(round(self.subtotal,2))
        if len(subtotal) > 9:
            subtotal = '{:>9}'.format('******')
        return subtotal

    def get_pv_subtotal_str(self):
        subtotal = '{:>9}'.format(round(self.subtotal - self.descuento, 2))
        if len(subtotal) > 9:
            subtotal = '{:>9}'.format('******')
        return subtotal

    def get_pv_tarifa_cero_str(self):
        subtotal_cero = '{:>9}'.format(round(self.subtotal_cero - self.descuento_iva, 2))
        if len(subtotal_cero) > 9:
            subtotal_cero = '{:>9}'.format('******')
        return subtotal_cero

    def get_pv_tarifa_iva_str(self):
        subtotal_iva = '{:>9}'.format(round(self.subtotal_iva - self.descuento_cero, 2))
        if len(subtotal_iva) > 9:
            subtotal_iva = '{:>9}'.format('******')
        return subtotal_iva

    def get_pv_impuesto_str(self):
        impuesto = '{:>9}'.format(round(self.impuesto, 2))
        if len(impuesto) > 9:
            impuesto = '{:>9}'.format('******')
        return impuesto

    def get_pv_descuento_str(self):
        descuento = '{:>9}'.format(round(self.descuento, 2))
        if len(descuento) > 9:
            descuento = '{:>9}'.format('******')
        return descuento

    def get_pv_total_str(self):
        total = '{:>9}'.format(round(self.total, 2))
        if len(total) > 9:
            total = '{:>9}'.format('******')
        return total

    def get_pv_creadopor_str(self):
        return '{:<12}'.format(self.creadopor)

    def get_pv_caja_cod_str(self):
        return '{:<12}'.format(self.caja.codigo)

    def get_pv_hora_str(self):
        return '{}'.format(self.creadodate.strftime("%H:%M"))

    def get_pv_bodega_str(self):
        bodega = 'BODEGA:{}-{}'.format(self.bodega.codigo,self.bodega.nombre)
        return '{:^30s}'.format(bodega)

    def get_pv_efectivo_str(self):
        efectivo = '{:>8}'.format(round(self.efectivo, 2))
        if len(efectivo) > 8:
            efectivo = '{:>8}'.format('******')
        return efectivo

    def get_pv_cambio_str(self):
        cambio = '{:>7}'.format(round(self.efectivo - self.total, 2))
        if len(cambio) > 7:
            cambio = '{:>7}'.format('******')
        return cambio

class VenFacturasDetalle(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    factura = models.ForeignKey('VenFacturas', models.DO_NOTHING, db_column='FacturaID')  # Field name made lowercase.
    ordendtid = models.CharField(db_column='OrdenDTID', max_length=10, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    producto = models.ForeignKey('inventario.InvProductos', models.DO_NOTHING, db_column='ProductoID')  # Field name made lowercase.
    bodega = models.ForeignKey('inventario.InvBodegas', models.DO_NOTHING,db_column='BodegaID')  # Field name made lowercase.
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=11, decimal_places=2,default=0)  # Field name made lowercase.
    devuelto = models.DecimalField(db_column='Devuelto', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    facturado = models.DecimalField(db_column='Facturado', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    entregado = models.DecimalField(db_column='Entregado', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    precio = models.DecimalField(db_column='Precio', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    costo = models.DecimalField(db_column='Costo', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    subtotal = models.DecimalField(db_column='Subtotal', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    tasa_descuento = models.DecimalField(db_column='TasaDescuento', max_digits=5, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    descuento = models.DecimalField(db_column='Descuento', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    tasa_financiero = models.DecimalField(db_column='TasaFinanciero', max_digits=5, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    financiero = models.DecimalField(db_column='Financiero', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    tasa_especial = models.DecimalField(db_column='TasaEspecial', max_digits=5, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    especial = models.DecimalField(db_column='Especial', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    tasa_impuesto = models.DecimalField(db_column='TasaImpuesto', max_digits=5, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    impuesto = models.DecimalField(db_column='Impuesto', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    total = models.DecimalField(db_column='Total', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    cupones = models.DecimalField(db_column='Cupones', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    clase = models.CharField(db_column='Clase', max_length=2, blank=True, null=True,default='')  # Field name made lowercase.
    empaque = models.CharField(db_column='Empaque', max_length=40, blank=True, null=True,default='')  # Field name made lowercase.
    embarque = models.BooleanField(db_column='Embarque', blank=True, null=True,default=False)  # Field name made lowercase.
    precio_name = models.CharField(db_column='PrecioName', max_length=40, blank=True, null=True,default='')  # Field name made lowercase.
    factor = models.DecimalField(db_column='Factor', max_digits=6, decimal_places=2,default=1)  # Field name made lowercase.
    detalle_ex = models.CharField(db_column='Detalle_Ex', max_length=1024,default='')  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(auto_now_add=True,db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(auto_now=True,db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    unidades = models.DecimalField(db_column='Unidades', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    tasa_credito = models.DecimalField(db_column='TasaCrédito', max_digits=6, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    valor_cupon = models.DecimalField(db_column='ValorCupón', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    valor_rentabilidad = models.DecimalField(db_column='ValorRentabilidad', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    valor_comision = models.DecimalField(db_column='ValorComision', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.producto.nombre)

    class Meta:
        verbose_name = 'Factura Detalle'
        verbose_name_plural = 'Factura Detalles'
        managed = False
        db_table = 'VEN_FACTURAS_DT'

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
            else:
                self.editadopor = user.username
        except:
            pass
        super(VenFacturasDetalle, self).save(force_insert, force_update, using)

    def get_pv_cantidad_str(self):
        cantidad = '{:>5}'.format(round(self.cantidad/self.factor,2))
        if len(cantidad) > 5:
            cantidad = '{:>5}'.format('***')
        return cantidad

    def get_pv_producto_str(self):
        return '{:<15}'.format(self.producto.nombre_corto)

    def get_pv_precio_unitario_str(self):
        precio = '{:>6}'.format(round((self.total/(self.cantidad/self.factor)),2))
        if len(precio) >6:
            precio = '{:>6}'.format('***')
        return precio

    def get_pv_total_str(self):
        total = '{}{}'.format(round(self.total,2),'*' if self.impuesto > 0 else '')
        total = '{:>6}'.format(total)
        if len(total) > 6:
            total = '{:>6}'.format('***')
        return total

class VenLiquidacionComision(models.Model):
    numero = models.CharField(max_length=10,editable=False)
    fecha = models.DateTimeField(default=now)
    tipo = models.CharField(max_length=10,choices=TIPO_DOCUMENTO_COMISION,blank=True, null=True)
    ruc = models.CharField(max_length=13, blank=True, null=True)
    asientoid = models.CharField(max_length=10, default='', editable=False)
    vendedor = models.ForeignKey(EmpEmpleados,on_delete=models.PROTECT,max_length=10)
    divisaid = models.CharField(max_length=10,blank=True, null=True,default='0000000001')
    cambio = models.DecimalField(max_digits=12, decimal_places=6, default=1)
    subtotal = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True,default=0)
    descuento = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True,default=0)
    impuesto = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True,default=0)
    total = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True,default=0)
    detalle = models.CharField(max_length=100, blank=True, null=True)
    pagada = models.BooleanField(default=False)

    comision_pendiente = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,default=0)
    ventas_nuevas = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,default=0)
    comision_totales = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,default=0)
    liquidacion_parcial= models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,default=0)
    liquidacion_total= models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,default=0)
    liquidacion_pendiente= models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,default=0)
    liquidacion_supervicion= models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,default=0)

    anulado = models.BooleanField(default=False)
    creadopor = models.CharField(max_length=15, blank=True, null=True,editable=False)
    creadodate = models.DateTimeField(auto_now_add=True,blank=True, null=True,editable=False)
    editadopor = models.CharField(max_length=15, blank=True, null=True,editable=False)
    editadodate = models.DateTimeField(auto_now=True, blank=True, null=True,editable=False)
    sucursalid = models.CharField(max_length=2, blank=True, null=True,editable=False)
    divisionid = models.CharField(max_length=10, blank=True, null=True,editable=False)
    pcid = models.CharField(max_length=50, blank=True, null=True, editable=False,default='')

    def __str__(self):
        return '{}'.format(self.fecha)

    class Meta:
        verbose_name = 'Liquidación de comisión'
        verbose_name_plural = 'Liquidación de comisiones'
        ordering = ('-fecha',)

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        add = False
        try:
            user = get_current_user()
            if self._state.adding:
                add = True
                self.creadopor = user.username
                self.sucursalid = user.segusuarioparametro.sucursal.codigo
                self.divisionid = user.segusuarioparametro.banco.division_id
            else:
                self.editadopor = user.username
        except:
            pass
        super(VenLiquidacionComision, self).save(force_insert, force_update, using)
        if add:
            try:
                self.numero = str(self.id).zfill(10)
            except:
                pass
            super(VenLiquidacionComision, self).save()

class VenLiquidacionComisionDetalle(models.Model):
    comision = models.ForeignKey(VenLiquidacionComision, on_delete=models.PROTECT)
    numcartilla = models.CharField(max_length=15, blank=True, null=True)
    cliente = models.ForeignKey(CliClientes, on_delete=models.PROTECT, max_length=10, blank=True, null=True)
    factura = models.ForeignKey(VenFacturas, on_delete=models.PROTECT, max_length=10)
    contado = models.BooleanField(default=False)
    fecha = models.DateTimeField(default=now,blank=True, null=True)
    valor_credito = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    valor_comision = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    valor_pago = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    valor_abono = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True,default=0)
    saldo = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True,default=0)
    abonos = models.IntegerField(default=0)
    dias = models.IntegerField(default=0)
    porcentaje = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True,default=0)

    supervisor = models.ForeignKey(EmpEmpleados, on_delete=models.PROTECT, max_length=10,blank=True, null=True)
    detalle = models.CharField(max_length=200,blank=True,null=True)
    estado = models.CharField(max_length=1,choices=ESTADO_COMISION,blank=True, null=True)
    anulado = models.BooleanField(default=False)
    creadopor = models.CharField(max_length=15, blank=True, null=True, editable=False)
    creadodate = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)
    editadopor = models.CharField(max_length=15, blank=True, null=True, editable=False)
    editadodate = models.DateTimeField(auto_now=True, blank=True, null=True, editable=False)
    sucursalid = models.CharField(max_length=2, blank=True, null=True, editable=False)
    divisionid = models.CharField(max_length=10, blank=True, null=True, editable=False)
    pcid = models.CharField(max_length=50, blank=True, null=True, editable=False, default='')

    def __str__(self):
        return '{}'.format(self.fecha)

    class Meta:
        verbose_name = 'Liquidación de comisión detalle'
        verbose_name_plural = 'Liquidación de comisiones detalle'
        ordering = ('-fecha',)

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
                self.sucursalid = user.segusuarioparametro.sucursal.codigo
            else:
                self.editadopor = user.username
        except:
            pass
        super(VenLiquidacionComisionDetalle, self).save(force_insert, force_update, using)

class VenLiquidacionComisionTemporal(models.Model):
    numero = models.CharField(max_length=10,editable=False)
    fecha = models.DateTimeField(default=now)
    tipo = models.CharField(max_length=10,choices=TIPO_DOCUMENTO_COMISION,blank=True, null=True)
    ruc = models.CharField(max_length=13, blank=True, null=True)
    asientoid = models.CharField(max_length=10, default='', editable=False)
    vendedor = models.ForeignKey(EmpEmpleados,on_delete=models.PROTECT,max_length=10)
    divisaid = models.CharField(max_length=10,blank=True, null=True,default='0000000001')
    cambio = models.DecimalField(max_digits=12, decimal_places=6, default=1)
    subtotal = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True,default=0)
    descuento = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True,default=0)
    impuesto = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True,default=0)
    total = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True,default=0)
    detalle = models.CharField(max_length=100, blank=True, null=True)
    pagada = models.BooleanField(default=False)

    comision_pendiente = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    ventas_nuevas = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    comision_totales = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    liquidacion_parcial = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    liquidacion_total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    liquidacion_pendiente = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    liquidacion_supervicion = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)

    anulado = models.BooleanField(default=False)
    creadopor = models.CharField(max_length=15, blank=True, null=True,editable=False)
    creadodate = models.DateTimeField(auto_now_add=True,blank=True, null=True,editable=False)
    editadopor = models.CharField(max_length=15, blank=True, null=True,editable=False)
    editadodate = models.DateTimeField(auto_now=True, blank=True, null=True,editable=False)
    sucursalid = models.CharField(max_length=2, blank=True, null=True,editable=False)
    divisionid = models.CharField(max_length=10, blank=True, null=True,editable=False)
    pcid = models.CharField(max_length=50, blank=True, null=True, editable=False,default='')

    def __str__(self):
        return '{}'.format(self.fecha)

    class Meta:
        verbose_name = 'Liquidación de comisión temporal'
        verbose_name_plural = 'Liquidación de comisiones temporal'
        ordering = ('-fecha',)

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        add = False
        try:
            user = get_current_user()
            if self._state.adding:
                add = True
                self.creadopor = user.username
                self.sucursalid = user.segusuarioparametro.sucursal.codigo
                self.divisionid = user.segusuarioparametro.banco.division_id
            else:
                self.editadopor = user.username
        except:
            pass
        super(VenLiquidacionComisionTemporal, self).save(force_insert, force_update, using)
        if add:
            try:
                self.numero = str(self.id).zfill(10)
            except:
                pass
            super(VenLiquidacionComisionTemporal, self).save()

class VenLiquidacionComisionDetalleTemporal(models.Model):
    comision = models.ForeignKey(VenLiquidacionComisionTemporal, on_delete=models.PROTECT)
    movimientoid = models.CharField(max_length=10,blank=True,null=True)
    numcartilla = models.CharField(max_length=15, blank=True, null=True)
    cliente = models.ForeignKey(CliClientes, on_delete=models.PROTECT, max_length=10, blank=True, null=True)
    factura = models.ForeignKey(VenFacturas, on_delete=models.PROTECT, max_length=10)
    contado = models.BooleanField(default=False)
    fecha = models.DateTimeField(default=now,blank=True, null=True)
    valor_credito = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    valor_comision = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    valor_pago = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    valor_abono = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    valor_pagado = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    saldo = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    abonos = models.IntegerField(default=0)
    dias = models.IntegerField(default=0)
    porcentaje = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    supervisor = models.ForeignKey(EmpEmpleados, on_delete=models.PROTECT, max_length=10,blank=True, null=True)
    detalle = models.CharField(max_length=200,blank=True,null=True)
    estado = models.CharField(max_length=1,choices=ESTADO_COMISION,blank=True, null=True)
    procesar =models.BooleanField(default=False)
    anulado = models.BooleanField(default=False)
    creadopor = models.CharField(max_length=15, blank=True, null=True, editable=False)
    creadodate = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)
    editadopor = models.CharField(max_length=15, blank=True, null=True, editable=False)
    editadodate = models.DateTimeField(auto_now=True, blank=True, null=True, editable=False)
    sucursalid = models.CharField(max_length=2, blank=True, null=True, editable=False)
    divisionid = models.CharField(max_length=10, blank=True, null=True, editable=False)
    pcid = models.CharField(max_length=50, blank=True, null=True, editable=False, default='')

    def __str__(self):
        return '{}'.format(self.fecha)

    class Meta:
        verbose_name = 'Liquidación de comisión detalle temporal'
        verbose_name_plural = 'Liquidación de comisiones detalle temporal'
        ordering = ('-fecha',)

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
                self.sucursalid = user.segusuarioparametro.sucursal.codigo
            else:
                self.editadopor = user.username
        except:
            pass
        super(VenLiquidacionComisionDetalleTemporal, self).save(force_insert, force_update, using)

class VenLiquidacionMovimientos(models.Model):
    fecha = models.DateTimeField(default=now)
    vendedor = models.ForeignKey(EmpEmpleados, on_delete=models.PROTECT, max_length=10)
    supervisorid = models.CharField(max_length=10, blank=True, null=True,default='')
    numcartilla = models.CharField(max_length=15, blank=True, null=True)
    cliente = models.ForeignKey(CliClientes, on_delete=models.PROTECT, max_length=10,blank=True, null=True)
    documentoid = models.CharField(max_length=10, blank=True, null=True,default='')
    contado = models.BooleanField(default=False)
    asientoid = models.CharField(max_length=10, blank=True, null=True,default='')
    numero = models.CharField(max_length=10, blank=True, null=True, editable=False)
    detalle = models.CharField(max_length=200,blank=True, null=True,default='')
    valor_credito = models.DecimalField(max_digits=19, decimal_places=4,default=0)
    valor = models.DecimalField(max_digits=19, decimal_places=4,default=0)
    valor_base = models.DecimalField(max_digits=19,decimal_places=4,default=0)
    movimiento = models.ForeignKey('self',on_delete=models.PROTECT,blank=True, null=True)
    divisaid = models.CharField(max_length=10,blank=True, null=True,default='0000000001')
    cambio = models.DecimalField(max_digits=12, decimal_places=6,default=1)
    saldo = models.DecimalField(max_digits=19, decimal_places=4,default=0)
    tipo = models.CharField(max_length=10, choices=TIPO_DOCUMENTO_COMISION,blank=True, null=True)
    tipo_modelo = models.CharField(max_length=10, blank=True, null=True,default='')
    credito = models.BooleanField(default=False)
    estado = models.CharField(max_length=1,choices=ESTADO_COMISION,blank=True, null=True)
    anulado = models.BooleanField(default=False)
    creadopor = models.CharField(max_length=15, blank=True, null=True,editable=False)
    creadodate = models.DateTimeField(auto_now_add=True,blank=True, null=True,editable=False)
    editadopor = models.CharField(max_length=15, blank=True, null=True,editable=False,default='')
    editadodate = models.DateTimeField(auto_now=True,blank=True, null=True,editable=False)
    anuladopor = models.CharField(max_length=15, blank=True, null=True,editable=False,default='')
    anuladodate = models.DateTimeField(blank=True, null=True,editable=False)
    anuladonota = models.CharField(max_length=1024, blank=True, null=True, editable=False,default='')
    sucursalid = models.CharField(max_length=2, blank=True, null=True,editable=False)
    divisionid = models.CharField(max_length=10, blank=True, null=True,editable=False)

    def __str__(self):
        return '{}'.format(self.fecha)

    class Meta:
        verbose_name = 'Liquidación movimiento'
        verbose_name_plural = 'Liquidación de movimientos'
        ordering = ('-fecha',)

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
                self.sucursalid = user.segusuarioparametro.sucursal.codigo
            else:
                self.editadopor = user.username
        except:
            pass

        super(VenLiquidacionMovimientos, self).save(force_insert, force_update, using)
