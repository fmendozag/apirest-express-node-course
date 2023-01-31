from crum import get_current_user
from django.db import models, connection

from cliente.models import CliClientesDeudas
from contabilidad.models import AccAsientos

class BanGrupos(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10, editable=False)  # Field name made lowercase.
    padre = models.ForeignKey('self', models.DO_NOTHING, db_column='PadreID', blank=True,
                              null=True)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    orden = models.CharField(db_column='Orden', max_length=1024, blank=True, null=True,
                             editable=False)  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=1024, blank=True, null=True,
                            editable=False)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado', default=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PCID', max_length=50, blank=True, null=True,
                            editable=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,
                                 editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,
                                       editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,
                                      editable=False)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Banco Grupo'
        verbose_name_plural = 'Banco Grupos'
        managed = False
        db_table = 'BAN_GRUPOS'

class BanBancos(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10, editable=False)  # Field name made lowercase.
    grupo = models.ForeignKey('BanGrupos', models.DO_NOTHING, db_column='GrupoID', blank=True,
                              null=True)  # Field name made lowercase.
    sucursal = models.CharField(db_column='Sucursal', max_length=2, blank=True, null=True)  # Field name made lowercase.
    division = models.ForeignKey('sistema.SisDivisiones', models.DO_NOTHING, db_column='DivisionID', max_length=10,
                                 blank=True, null=True)  # Field name made lowercase.
    bodega = models.ForeignKey('inventario.InvBodegas', models.DO_NOTHING, db_column='BodegaID', max_length=10,
                               blank=True, null=True)  # Field name made lowercase.
    ventas = models.IntegerField(db_column='Ventas', blank=True, null=True)  # Field name made lowercase.
    serie = models.CharField(db_column='Serie', max_length=7, blank=True, null=True)  # Field name made lowercase.
    cobertura = models.BooleanField(db_column='Cobertura', blank=True, null=True)  # Field name made lowercase.
    ctamayorid = models.CharField(db_column='CtaMayorID', max_length=10, blank=True,
                                  null=True)  # Field name made lowercase.
    ctaiccid = models.CharField(db_column='CtaICCID', max_length=10, blank=True,
                                null=True)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15, blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cuenta = models.CharField(db_column='Cuenta', max_length=50, blank=True, null=True)  # Field name made lowercase.
    clase = models.CharField(db_column='Clase', max_length=2, blank=True, null=True,
                             choices=(('01', '01'), ('02', '02')))  # Field name made lowercase.
    divisa = models.CharField(db_column='DivisaID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado', default=False)  # Field name made lowercase.
    formato_comprobante = models.CharField(db_column='Formato_Comprobante', max_length=1024, blank=True,
                                           null=True)  # Field name made lowercase.
    formato_cheque = models.CharField(db_column='Formato_Cheque', max_length=1024, blank=True,
                                      null=True)  # Field name made lowercase.
    www = models.CharField(db_column='WWW', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    ultimocheque = models.DecimalField(db_column='UltimoCheque', max_digits=6,
                                       decimal_places=0)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,
                                 editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,
                                      editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,
                                       editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PCID', max_length=50, blank=True, null=True,
                            editable=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    monto_maximo = models.DecimalField(db_column='MontoMáximo', max_digits=19, decimal_places=4, blank=True,
                                       null=True)  # Field name made lowercase.
    empleado = models.CharField(db_column='EmpleadoID', max_length=10, blank=True,
                                null=True)  # Field name made lowercase.
    activo_contado = models.BooleanField(db_column='ActivoContado', blank=True, null=True)  # Field name made lowercase.
    establecimiento_sri = models.CharField(db_column='Establecimiento_SRI', max_length=3, blank=True,null=True)  # Field name made lowercase.
    punto_venta_sri = models.CharField(db_column='PuntoVenta_SRI', max_length=3, blank=True,null=True)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Banco'
        verbose_name_plural = 'Bancos'
        managed = False
        db_table = 'BAN_BANCOS'

class BanIngresos(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10, editable=False)  # Field name made lowercase.
    banco = models.ForeignKey('BanBancos', models.DO_NOTHING, db_column='BancoID', blank=True,
                              null=True)  # Field name made lowercase.
    asientoid = models.CharField(db_column='AsientoID', max_length=10, blank=True,
                                 null=True)  # Field name made lowercase.
    deudor = models.ForeignKey('cliente.CliClientes', models.DO_NOTHING, db_column='DeudorID', max_length=10,
                               blank=True, null=True, default='')  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True, editable=False,
                            default='')  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10, blank=True, null=True,
                              editable=False)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha', blank=True, null=True)  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=100, default='')  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    rfir = models.DecimalField(db_column='RFIR', max_digits=19, decimal_places=4, blank=True,
                               null=True)  # Field name made lowercase.
    rfiva = models.DecimalField(db_column='RFIVA', max_digits=19, decimal_places=4, blank=True,
                                null=True)  # Field name made lowercase.
    valor = models.DecimalField(db_column='Valor', max_digits=19, decimal_places=4)  # Field name made lowercase.
    descuento = models.DecimalField(db_column='Descuento', max_digits=19, decimal_places=4, blank=True,
                                    null=True)  # Field name made lowercase.
    financiero = models.DecimalField(db_column='Financiero', max_digits=19, decimal_places=4, blank=True,
                                     null=True)  # Field name made lowercase.
    faltante = models.DecimalField(db_column='Faltante', max_digits=19, decimal_places=4, blank=True,
                                   null=True)  # Field name made lowercase.
    sobrante = models.DecimalField(db_column='Sobrante', max_digits=19, decimal_places=4, blank=True,
                                   null=True)  # Field name made lowercase.
    valor_base = models.DecimalField(db_column='Valor_Base', max_digits=19, decimal_places=4, blank=True,
                                     null=True)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado', default=False)  # Field name made lowercase.
    divisaid = models.CharField(db_column='DivisaID', max_length=10)  # Field name made lowercase.
    cambio = models.DecimalField(db_column='Cambio', max_digits=12, decimal_places=6)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True,
                            default='')  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    anuladodate = models.DateTimeField(db_column='AnuladoDate', blank=True, null=True,
                                       editable=False)  # Field name made lowercase.
    anuladonota = models.CharField(db_column='AnuladoNota', max_length=1024, blank=True, null=True,
                                   editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(auto_now=True, db_column='EditadoDate', blank=True, null=True,
                                       editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(auto_now_add=True, db_column='CreadoDate', blank=True, null=True,
                                      editable=False)  # Field name made lowercase.
    divisionid = models.CharField(db_column='DivisiónID', max_length=10, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    cajaid = models.CharField(db_column='CajaID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    relacionado = models.BooleanField(db_column='Relacionado', default=False)  # Field name made lowercase.
    cobradorid = models.CharField(db_column='CobradorID', max_length=10, blank=True,
                                  null=True)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.fecha)

    class Meta:
        verbose_name = 'Banco ingreso'
        verbose_name_plural = 'Banco ingresos'
        managed = False
        db_table = 'BAN_INGRESOS'

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
            else:
                self.editadopor = user.username
                self.actualizar_cobro()
        except:
            pass
        super(BanIngresos, self).save(force_insert, force_update, using)

    def actualizar_cobro(self):
        try:
            for dt in self.baningresosdetalle_set.all():
                dt.fecha = self.fecha
                dt.creadopor = self.creadopor
                dt.save()

            asiento = AccAsientos.objects.get(pk=self.asientoid)
            asiento.fecha = self.fecha
            asiento.creadopor = self.creadopor
            asiento.save()

            banco = BanBancos.objects.get(id=self.banco.id)
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE ACC_ASIENTOS_DT SET CuentaID=%s, CreadoPor=%s WHERE AsientoID=%s AND [Débito]=1 ",
                    (banco.ctamayorid, self.creadopor, asiento.id))


            for cd in CliClientesDeudas.objects.filter(anulado=False, documentoid=self.id, asientoid=asiento.id,tipo='CLI-IN'):
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE CLI_CLIENTES_DEUDAS SET Fecha =%s,Vencimiento=%s,CreadoPor=%s where ID=%s",
                                   [self.fecha, self.fecha, self.creadopor, cd.id])

            with connection.cursor() as cursor:
                cursor.execute("UPDATE BAN_BANCOS_CARDEX SET Fecha =%s,Fecha_Banco=%s,CreadoPor=%s where DocumentoID=%s AND Tipo='CLI-IN' AND [Débito]=1",
                               [self.fecha, self.fecha, self.creadopor, self.id])

        except Exception as e:
            pass

class BanIngresosDetalle(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10, editable=False)  # Field name made lowercase.
    ingreso = models.ForeignKey('BanIngresos', models.DO_NOTHING, db_column='IngresoID', blank=True,
                                null=True)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True, editable=False,
                            default='')  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10, blank=True, null=True, default='',
                              editable=False)  # Field name made lowercase.
    banco = models.CharField(db_column='Banco', max_length=30, blank=True, null=True)  # Field name made lowercase.
    cuenta = models.CharField(db_column='Cuenta', max_length=15, blank=True, null=True)  # Field name made lowercase.
    girador = models.CharField(db_column='Girador', max_length=30, blank=True, null=True,
                               default='')  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha', blank=True, null=True)  # Field name made lowercase.
    valor = models.DecimalField(db_column='Valor', max_digits=19, decimal_places=4, blank=True,
                                null=True)  # Field name made lowercase.
    valor_base = models.DecimalField(db_column='Valor_Base', max_digits=19, decimal_places=4, blank=True,
                                     null=True)  # Field name made lowercase.
    difencambio = models.DecimalField(db_column='DifenCambio', max_digits=19, decimal_places=4, blank=True,
                                      null=True)  # Field name made lowercase.
    depositado = models.DecimalField(db_column='Depositado', max_digits=19, decimal_places=4, blank=True, null=True,
                                     default=0)  # Field name made lowercase.
    divisaid = models.CharField(db_column='DivisaID', max_length=10, blank=True,
                                null=True)  # Field name made lowercase.
    cambio = models.DecimalField(db_column='Cambio', max_digits=12, decimal_places=6)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,
                                 editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(auto_now_add=True, db_column='CreadoDate', blank=True, null=True,
                                      editable=False)  # Field name made lowercase.
    numcartilla = models.CharField(db_column='NumCartilla', max_length=15, blank=True, null=True)
    recibopago = models.CharField(db_column='ReciboPago', max_length=20, blank=True,
                                  null=True)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.numero)

    class Meta:
        verbose_name = 'Banco ingreso detalle'
        verbose_name_plural = 'Banco ingreso detalles'
        managed = False
        db_table = 'BAN_INGRESOS_DT'

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
        except:
            pass
        super(BanIngresosDetalle, self).save(force_insert, force_update, using)

class BanIngresosDeudas(models.Model):
    ingresoid = models.CharField(db_column='IngresoID', max_length=10, blank=True,
                                 null=True)  # Field name made lowercase.
    deudaid = models.CharField(db_column='DeudaID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True, editable=False,
                            default='')  # Field name made lowercase.
    valor = models.DecimalField(db_column='Valor', max_digits=19, decimal_places=4)  # Field name made lowercase.
    cambio = models.DecimalField(db_column='Cambio', max_digits=12, decimal_places=6, blank=True,
                                 null=True)  # Field name made lowercase.
    divisaid = models.CharField(db_column='DivisaID', max_length=10, blank=True,
                                null=True)  # Field name made lowercase.
    saldo = models.DecimalField(db_column='Saldo', max_digits=19, decimal_places=4)  # Field name made lowercase.
    dif_cambio = models.DecimalField(db_column='Dif_Cambio', max_digits=19, decimal_places=4, blank=True,
                                     null=True)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha', blank=True, null=True)  # Field name made lowercase.
    vencimiento = models.DateTimeField(db_column='Vencimiento', blank=True, null=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10, blank=True, null=True)  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=100, blank=True, null=True)  # Field name made lowercase.
    credito = models.BooleanField(db_column='Crédito')  # Field name made lowercase.
    rubroid = models.CharField(db_column='RubroID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    ctacxcid = models.CharField(db_column='CtaCxCID', max_length=10, blank=True,
                                null=True)  # Field name made lowercase.
    cambiodia = models.DecimalField(db_column='CambioDia', max_digits=12, decimal_places=6, blank=True,
                                    null=True)  # Field name made lowercase.
    divisionid = models.CharField(db_column='DivisiónID', max_length=10, blank=True,
                                  null=True)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,
                                 editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(auto_now_add=True, db_column='CreadoDate', blank=True, null=True,
                                      editable=False)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.fecha)

    class Meta:
        verbose_name = 'Banco ingreso deuda'
        verbose_name_plural = 'Banco ingreso deudas'
        managed = False
        db_table = 'BAN_INGRESOS_DEUDAS'

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
        except:
            pass
        super(BanIngresosDeudas, self).save(force_insert, force_update, using)

class BanBancosCardex(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10, editable=False)  # Field name made lowercase.
    banco = models.ForeignKey(BanBancos, models.DO_NOTHING, db_column='BancoID', max_length=10, blank=True,
                              null=True)  # Field name made lowercase.
    documentoid = models.CharField(db_column='DocumentoID', max_length=10, blank=True, null=True,
                                   default='')  # Field name made lowercase.
    asientoid = models.CharField(db_column='AsientoID', max_length=10, blank=True, null=True,
                                 default='')  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,
                                  default='')  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,
                            default='')  # Field name made lowercase.
    divisaid = models.CharField(db_column='DivisaID', max_length=10, blank=True, null=True,
                                default='')  # Field name made lowercase.
    cambio = models.DecimalField(db_column='Cambio', max_digits=12, decimal_places=6,
                                 default=1)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha', blank=True, null=True)  # Field name made lowercase.
    fecha_banco = models.DateTimeField(db_column='Fecha_Banco', blank=True, null=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10, default='')  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=100, default='')  # Field name made lowercase.
    debito = models.BooleanField(db_column='Débito', default=False)  # Field name made lowercase.
    valor = models.DecimalField(db_column='Valor', max_digits=19, decimal_places=4,
                                default=0)  # Field name made lowercase.
    valor_base = models.DecimalField(db_column='Valor_Base', max_digits=19, decimal_places=4, blank=True, null=True,
                                     default=0)  # Field name made lowercase.
    conciliado = models.BooleanField(db_column='Conciliado', default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,
                                 default='')  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', auto_now_add=True, blank=True,
                                      null=True)  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10, blank=True, null=True,
                              default='')  # Field name made lowercase.
    cheque = models.CharField(db_column='Cheque', max_length=10, blank=True, null=True,
                              default='')  # Field name made lowercase.
    fecha_cheque = models.DateTimeField(db_column='Fecha_Cheque', blank=True, null=True)  # Field name made lowercase.
    beneficiario = models.CharField(db_column='Beneficiario', max_length=50, blank=True, null=True,
                                    default='')  # Field name made lowercase.
    divisionid = models.CharField(db_column='DivisiónID', max_length=10, blank=True, null=True,
                                  default='')  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado', default=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True,
                                  default='')  # Field name made lowercase.
    anuladodate = models.DateTimeField(db_column='AnuladoDate', blank=True, null=True)  # Field name made lowercase.
    anuladonota = models.CharField(db_column='AnuladoNota', max_length=1024, blank=True, null=True,
                                   default='')  # Field name made lowercase.
    secuencia = models.TextField(db_column='Secuencia', blank=True,
                                 null=True)  # Field name made lowercase. This field type is a guess.

    def __str__(self):
        return '{}'.format(self.fecha)

    class Meta:
        verbose_name = 'Banco cardex'
        verbose_name_plural = 'Banco cardex'
        managed = False
        db_table = 'BAN_BANCOS_CARDEX'
