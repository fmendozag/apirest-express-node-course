from crum import get_current_user
from django.db import models
from django.utils.timezone import now

class PosAperturaCaja(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha',default=now, blank=True, null=True)  # Field name made lowercase.
    numero = models.CharField(db_column='Número', unique=True, max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    caja = models.ForeignKey('banco.BanBancos', models.DO_NOTHING, db_column='CajaID', max_length=10, blank=True,null=True,default='')  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=100, blank=True, null=True,default='')  # Field name made lowercase.
    total = models.DecimalField(db_column='Total', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,default='')  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate',auto_now_add=True, blank=True, null=True)  # Field name made lowercase.
    cerrada = models.BooleanField(db_column='Cerrada',default=False)  # Field name made lowercase.
    cerradapor = models.CharField(db_column='CerradaPor', max_length=15, blank=True, null=True,default='')  # Field name made lowercase.
    cerradadate = models.DateTimeField(db_column='CerradaDate',auto_now=True,blank=True, null=True)  # Field name made lowercase.
    ingresoid = models.CharField(db_column='IngresoID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    fecha_cierre = models.DateTimeField(db_column='FechaCierre', blank=True, null=True)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    sobrante = models.DecimalField(db_column='Sobrante', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    faltante = models.DecimalField(db_column='Faltante', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.detalle)

    class Meta:
        verbose_name = 'Apertura de caja'
        verbose_name_plural = 'Aperturas caja'
        managed = False
        db_table = 'POS_APERTURA_CAJA'

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
            else:
                self.cerradapor = user.username
        except:
            pass
        super(PosAperturaCaja, self).save(force_insert, force_update, using)

class PosCierre(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10,blank=True, null=True,default='')  # Field name made lowercase.
    caja = models.ForeignKey('banco.BanBancos', models.DO_NOTHING, db_column='CajaID', max_length=10, blank=True,null=True,default='')  # Field name made lowercase.
    usuarioid = models.CharField(db_column='UsuarioID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha', blank=True, null=True)  # Field name made lowercase.
    fecha_cierre = models.DateTimeField(db_column='FechaCierre', blank=True, null=True)  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=100,default='')  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=100, blank=True, null=True,default='')  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    apertura = models.DecimalField(db_column='Apertura', max_digits=19, decimal_places=4, default=0)  # Field name made lowercase.
    facturas = models.DecimalField(db_column='Facturas', max_digits=19, decimal_places=4, default=0)  # Field name made lowercase.
    ordenes = models.DecimalField(db_column='Ordenes', max_digits=19, decimal_places=4, default=0)  # Field name made lowercase.
    cobranzas = models.DecimalField(db_column='Cobranzas', max_digits=19, decimal_places=4, default=0)  # Field name made lowercase.
    devolucion_contado = models.DecimalField(db_column='DevolucionContado', max_digits=19, decimal_places=4, default=0)  # Field name made lowercase.
    devolucion_credito = models.DecimalField(db_column='DevolucionCredito', max_digits=19, decimal_places=4, default=0)  # Field name made lowercase.
    egresos = models.DecimalField(db_column='Egresos', max_digits=19, decimal_places=4, default=0)  # Field name made lowercase.
    creditos = models.DecimalField(db_column='Creditos', max_digits=19, decimal_places=4, default=0)  # Field name made lowercase.
    tarjetas = models.DecimalField(db_column='Tarjetas', max_digits=19, decimal_places=4, default=0)  # Field name made lowercase.
    transferencias = models.DecimalField(db_column='Transferencias', max_digits=19, decimal_places=4, default=0)  # Field name made lowercase.
    efectivo = models.DecimalField(db_column='Efectivo', max_digits=19, decimal_places=4, default=0)  # Field name made lowercase.
    total_ventas = models.DecimalField(db_column='TotalVentas', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    total_contado = models.DecimalField(db_column='TotalContado', max_digits=19, decimal_places=4, default=0)  # Field name made lowercase.
    total_credito = models.DecimalField(db_column='TotalCredito', max_digits=19, decimal_places=4, default=0)  # Field name made lowercase.
    estado = models.CharField(db_column='Estado', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    total = models.DecimalField(db_column='Total', max_digits=19, decimal_places=4, default=0)  # Field name made lowercase.
    caja_envio = models.ForeignKey('banco.BanBancos', models.DO_NOTHING, db_column='CajaEnvioID', max_length=10, blank=True,null=True, default='',related_name='caja_envio_id')  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,default='')  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate',auto_now_add=True, blank=True, null=True)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True,default='')  # Field name made lowercase.
    anuladodate = models.DateTimeField(db_column='AnuladoDate', blank=True, null=True)  # Field name made lowercase.
    anuladonota = models.CharField(db_column='AnuladoNota', max_length=1024, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    ingresoid = models.CharField(db_column='IngresoID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    asientoid = models.CharField(db_column='AsientoID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.detalle)

    class Meta:
        verbose_name = 'Cierre de caja'
        verbose_name_plural = 'Cierres de cajas'
        managed = False
        db_table = 'POS_CIERRE'


    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
        except:
            pass
        super(PosCierre, self).save(force_insert, force_update, using)
