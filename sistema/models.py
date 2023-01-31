from crum import get_current_user
from django.db import models
from contadores.fn_contador import get_contador

class SisDivisiones(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15, blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50, blank=True, null=True)  # Field name made lowercase.
    gerente = models.CharField(db_column='Gerente', max_length=50, blank=True, null=True)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate',auto_now_add=True, blank=True, null=True)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', auto_now=True,blank=True, null=True)  # Field name made lowercase.
    sucursal = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PCID', max_length=50, blank=True, null=True,editable=False)  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    orden = models.CharField(db_column='Orden', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    informal = models.BooleanField(db_column='Informal', default=False)  # Field name made lowercase.
    activatefe = models.BooleanField(db_column='ActivateFE', default=False)  # Field name made lowercase.
    activatend = models.BooleanField(db_column='ActivateND', default=False)  # Field name made lowercase.
    activategu = models.BooleanField(db_column='ActivateGU', default=False)  # Field name made lowercase.
    activatere = models.BooleanField(db_column='ActivateRE', default=False)  # Field name made lowercase.
    ambiente_sri = models.BooleanField(db_column='AmbienteSRI', default=False)  # Field name made lowercase.
    facturacion_automatica_sri = models.BooleanField(db_column='FacturaciónAutomaticaSRI', default=False)  # Field name made lowercase.
    nombre_comercial_sri = models.CharField(db_column='NombreComercialSRI', max_length=200, blank=True, null=True)  # Field name made lowercase.
    razon_social_sri = models.CharField(db_column='RazonSocialSRI', max_length=200, blank=True, null=True)  # Field name made lowercase.
    ruc_sri = models.CharField(db_column='RucSRI', max_length=13, blank=True, null=True)  # Field name made lowercase.
    direccion_matriz_sri = models.CharField(db_column='DirecciónMatrizSRI', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    direccion_establecimiento_sri = models.CharField(db_column='DirecciónEstablecimientoSRI', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    contribuyente_especial_sri = models.CharField(db_column='ContribuyenteEspecialSRI', max_length=50, blank=True, null=True)  # Field name made lowercase.
    path_logo = models.CharField(db_column='PathLogo', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    path_certificado = models.CharField(db_column='PathCertificado', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    password_certificado_sri = models.CharField(db_column='PasswordCertificadoSRI', max_length=30, blank=True, null=True)  # Field name made lowercase.
    path_xml_generados = models.CharField(db_column='PathXMLGenerados', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    path_xml_autorizados = models.CharField(db_column='PathXMLAutorizados', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    servidor_correo = models.CharField(db_column='ServidorCorreo', max_length=30, blank=True, null=True)  # Field name made lowercase.
    cuenta_correo = models.CharField(db_column='CuentaCorreo', max_length=200, blank=True, null=True)  # Field name made lowercase.
    password_correo = models.CharField(db_column='PasswordCorreo', max_length=30, blank=True, null=True)  # Field name made lowercase.
    puerto_correo = models.CharField(db_column='PuertoCorreo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    activate_outlook = models.BooleanField(db_column='ActivateOutlook',default=False)  # Field name made lowercase.
    obligado_contabilidad = models.BooleanField(db_column='ObligadoContabilidad',default=False)  # Field name made lowercase.
    server_url = models.CharField(db_column='ServerURL',max_length=200,blank=True, null=True)  # Field name made lowercase.
    usuario_sri = models.CharField(db_column='UsuarioSRI',max_length=50,blank=True, null=True)  # Field name made lowercase.
    api_sri = models.CharField(db_column='ApiSRI',max_length=100,blank=True, null=True)
    # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Division'
        verbose_name_plural = 'Divisiones'
        managed = False
        db_table = 'SIS_DIVISIONES'

class SisZonas(models.Model):
    TIPO_ZONA = (
        ('PAIS      ', 'PAIS'),
        ('PROVINCIA ', 'PROVINCIA'),
        ('CIUDAD    ', 'CIUDAD'),
        ('CANTON    ', 'CANTON'),
        ('PARROQUIA ', 'PARROQUIA'),
        ('ZONAS     ', 'ZONA'),
        ('OTRO      ', 'OTRO'),
    )
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', unique=True, max_length=15)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10,choices=TIPO_ZONA,default='PAIS      ',blank=True, null=True)  # Field name made lowercase.
    padre = models.ForeignKey('self',db_column='PadreID',on_delete=models.PROTECT, max_length=10, blank=True, null=True)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    orden = models.CharField(db_column='Orden', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,
                                 editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', auto_now_add=True, blank=True,
                                      null=True)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', auto_now=True, blank=True,
                                       null=True)  # Field name made lowercase.
    sucursal = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,
                                editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PCID', max_length=50, blank=True, null=True,
                            editable=False)  # Field name made lowercase.
    sigla = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.codigo,self.nombre)

    class Meta:
        verbose_name = 'Zona'
        verbose_name_plural = 'Zonas'
        managed = False
        db_table = 'SIS_ZONAS'
        ordering = ['codigo']


    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.codigo:
            self.codigo = self.codigo.upper()

        if self.nombre:
            self.nombre = self.nombre.upper()

        if self.sigla:
            self.sigla = self.sigla.upper()

        try:
            user = get_current_user()
            if self._state.adding:
                self.id = get_contador('SIS_ZONAS-ID',user)
                self.creadopor = user.username
            else:
                self.editadopor = user.username
        except:
            pass

        super(SisZonas, self).save(force_insert, force_update, using)

        if not self.padre is None:
            self.ruta = self.padre.ruta + '/' + self.id
            self.orden = self.padre.orden + '/' + str(self.nombre)
        else:
            self.ruta = 'ROOT/' + self.id
            self.orden = 'General/' + str(self.nombre)

        super(SisZonas, self).save()

class SisSucursales(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=2)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True)  # Field name made lowercase.
    sucursal = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True)  # Field name made lowercase.
    pcid = models.CharField(db_column='PCID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    disponible = models.BooleanField(db_column='Disponible', blank=True, null=True)  # Field name made lowercase.
    serversql = models.CharField(db_column='ServerSQL', max_length=50, blank=True, null=True)  # Field name made lowercase.
    databasesql = models.CharField(db_column='DataBaseSQL', max_length=50, blank=True, null=True)  # Field name made lowercase.
    passwordsql = models.CharField(db_column='PasswordSQL', max_length=50, blank=True, null=True)  # Field name made lowercase.
    matriz = models.BooleanField(db_column='Matriz', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'
        managed = False
        db_table = 'SIS_SUCURSALES'

class SisParametros(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=50)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    valor = models.CharField(db_column='Valor', max_length=100, blank=True, null=True)  # Field name made lowercase.
    extradata = models.CharField(db_column='ExtraData', max_length=1024, blank=True, null=True)
    padre = models.ForeignKey('self', models.DO_NOTHING, db_column='PadreID', blank=True, null=True)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    orden = models.CharField(db_column='Orden', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True)  # Field name made lowercase.
    sucursal = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True)  # Field name made lowercase.
    pcid = models.CharField(db_column='PCID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    extra_sri = models.CharField(db_column='ExtraSRI', max_length=50, blank=True, null=True)
    cod_extra_sri = models.CharField(db_column='CodExtraSRI', max_length=15, blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Parametro'
        verbose_name_plural = 'Parametros'
        managed = False
        db_table = 'SIS_PARAMETROS'

class SisDivisas(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    simbolo = models.CharField(db_column='Símbolo', max_length=5, blank=True, null=True)  # Field name made lowercase.
    base = models.BooleanField(db_column='Base',default=False)  # Field name made lowercase.
    cambio = models.DecimalField(db_column='Cambio', max_digits=12, decimal_places=6, blank=True, null=True)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PCID', max_length=50, blank=True, null=True,editable=False,default='')  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Divisa'
        verbose_name_plural = 'Divisas'
        managed = False
        db_table = 'SIS_DIVISAS'
