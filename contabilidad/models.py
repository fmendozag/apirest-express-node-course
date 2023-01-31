from crum import get_current_user
from django.db import models

# Create your models here.
class AccCuentas(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=25)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    clase = models.CharField(db_column='Clase', max_length=2)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10)  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    orden = models.CharField(db_column='Orden', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    padre = models.ForeignKey('self', models.DO_NOTHING, db_column='PadreID', blank=True, null=True,default='')  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    exportado = models.BooleanField(db_column='Exportado',default=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PCID', max_length=50, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(auto_now_add=True,db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(auto_now=True,db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    debitos = models.CharField(db_column='Debitos', max_length=20, blank=True, null=True)  # Field name made lowercase.
    creditos = models.CharField(db_column='Creditos', max_length=20, blank=True, null=True)  # Field name made lowercase.
    flujo_efectivo = models.DecimalField(db_column='FlujoEfectivo', max_digits=1, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    superavit = models.DecimalField(db_column='SuperAvit', max_digits=1, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    agrupado = models.BooleanField(db_column='Agrupado', blank=True, null=True)  # Field name made lowercase.
    estado_cuenta = models.BooleanField(db_column='EstadoCuenta', blank=True, null=True,default=False)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Cuenta contable'
        verbose_name_plural = 'Cuentas contable'
        managed = False
        db_table = 'ACC_CUENTAS'

class AccAsientos(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    documentoid = models.CharField(db_column='DocumentoID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha')  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=100)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True,default='')  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    pendiente = models.BooleanField(db_column='Pendiente',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PCID', max_length=50, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(auto_now_add=True,db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(auto_now=True,db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladodate = models.DateTimeField(db_column='AnuladoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladonota = models.CharField(db_column='AnuladoNota', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    divisionid = models.CharField(db_column='DivisiónID', max_length=10, blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.numero)

    class Meta:
        verbose_name = 'Asiento'
        verbose_name_plural = 'Asientos'
        managed = False
        db_table = 'ACC_ASIENTOS'

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
            else:
                self.editadopor = user.username
        except:
            pass
        super(AccAsientos, self).save(force_insert, force_update, using)

class AccAsientosDetalle(models.Model):
    asiento = models.ForeignKey('AccAsientos', models.DO_NOTHING, db_column='AsientoID', blank=True, null=True)  # Field name made lowercase.
    cuenta = models.ForeignKey('AccCuentas', models.DO_NOTHING, db_column='CuentaID', blank=True, null=True)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    debito = models.BooleanField(db_column='Débito',default=False)  # Field name made lowercase.
    valor = models.DecimalField(db_column='Valor', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=250, blank=True, null=True,default='')  # Field name made lowercase.
    pcid = models.CharField(db_column='PCID', max_length=50, blank=True, null=True,editable=False)  # Field name made lowercase.
    valor_base = models.DecimalField(db_column='Valor_Base', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    divisaid = models.CharField(db_column='DivisaID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    cambio = models.DecimalField(db_column='Cambio', max_digits=12, decimal_places=6,default=0)  # Field name made lowercase.
    creadodate = models.DateTimeField(auto_now_add=True,db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    secuencia = models.TextField(db_column='Secuencia')  # Field name made lowercase. This field type is a guess.
    registro = models.DecimalField(db_column='Registro', max_digits=5, decimal_places=0, blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.detalle)

    class Meta:
        verbose_name = 'Asiento detalle'
        verbose_name_plural = 'Asientos detalle'
        managed = False
        db_table = 'ACC_ASIENTOS_DT'

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
        except:
            pass
        super(AccAsientosDetalle, self).save(force_insert, force_update, using)

