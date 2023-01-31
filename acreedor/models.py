from crum import get_current_user
from django.db import models

# Create your models here.
class AcrGrupos(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    padre= models.ForeignKey('self', models.DO_NOTHING, db_column='PadreID', blank=True, null=True)   # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    orden = models.CharField(db_column='Orden', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,editable=False)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Acreedor Grupo'
        verbose_name_plural = 'Acreedor Grupos'
        managed = False
        db_table = 'ACR_GRUPOS'

class AcrAcreedores(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    grupo = models.ForeignKey('AcrGrupos', models.DO_NOTHING,db_column='GrupoID', blank=True, null=True)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50, blank=True, null=True)  # Field name made lowercase.
    representante = models.CharField(db_column='Representante', max_length=60, blank=True, null=True)  # Field name made lowercase.
    terminoid = models.CharField(db_column='TérminoID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    zonaid = models.CharField(db_column='ZonaID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    telefono1 = models.CharField(db_column='Teléfono1', max_length=20, blank=True, null=True)  # Field name made lowercase.
    telefono2 = models.CharField(db_column='Teléfono2', max_length=20, blank=True, null=True)  # Field name made lowercase.
    telefono3 = models.CharField(db_column='Teléfono3', max_length=20, blank=True, null=True)  # Field name made lowercase.
    telefono4 = models.CharField(db_column='Teléfono4', max_length=20, blank=True, null=True)  # Field name made lowercase.
    direccion = models.CharField(db_column='Dirección', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=50, blank=True, null=True)  # Field name made lowercase.
    www = models.CharField(db_column='WWW', max_length=50, blank=True, null=True)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    ruc = models.CharField(db_column='Ruc', max_length=13, blank=True, null=True)  # Field name made lowercase.
    cedula = models.CharField(db_column='Cédula', max_length=10, blank=True, null=True)  # Field name made lowercase.
    clase = models.CharField(db_column='Clase', max_length=2, blank=True, null=True)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    secuenciaid = models.CharField(db_column='SecuenciaID', max_length=10, blank=True, null=True,editable=False)  # Field name made lowercase.
    utorizacion = models.CharField(db_column='acrAutorizacion', max_length=100, blank=True, null=True)  # Field name made lowercase.
    serie = models.CharField(db_column='acrSerie', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tipo_cuenta = models.CharField(db_column='TipoCuenta', max_length=2, blank=True, null=True)  # Field name made lowercase.
    cuenta = models.CharField(db_column='Cuenta', max_length=50, blank=True, null=True)  # Field name made lowercase.
    bancoid = models.CharField(db_column='BancoID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    copia_email = models.CharField(db_column='CopiaEmail', max_length=50, blank=True, null=True)  # Field name made lowercase.
    tipo_acreedor = models.DecimalField(db_column='TipoAcreedor', max_digits=1, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    cta_contable = models.CharField(db_column='CtaContable', max_length=25, blank=True, null=True)  # Field name made lowercase.
    frecuenciavisita = models.DecimalField(db_column='FrecuenciaVisita', max_digits=8, decimal_places=2, blank=True,null=True,default=0)  # Field name made lowercase.
    plazoentregaminimo = models.DecimalField(db_column='PlazoEntregaMinimo', max_digits=8, decimal_places=2, blank=True,null=True,default=0)  # Field name made lowercase.
    plazoentregamaximo = models.DecimalField(db_column='PlazoEntregaMaximo', max_digits=8, decimal_places=2, blank=True,null=True,default=0)  # Field name made lowercase.
    promedioentrega = models.DecimalField(db_column='PromedioEntrega', max_digits=8, decimal_places=4, blank=True,null=True,default=0)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Acreedor'
        verbose_name_plural = 'Acreedores'
        managed = False
        db_table = 'ACR_ACREEDORES'

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
            else:
                self.editadopor = user.username
                self.promedioentrega = round((self.plazoentregaminimo + self.plazoentregamaximo)/2,2)
        except:
            pass
        super(AcrAcreedores, self).save(force_insert, force_update, using)
