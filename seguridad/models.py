from crum import get_current_user
from django.contrib.auth.models import User, Group, AbstractUser
from django.db import models
from banco.models import BanBancos
from cliente.models import CliGrupos
from sistema.models import SisSucursales, SisDivisiones

class SegModulo(models.Model):
    CLASE_RECURSO = (
        ('LISTA', 'LISTA'),
        ('ITEM', 'ITEM'),
    )
    TIPO_RECURSO = (
        ('Mantenimientos', 'MANTENIMIENTOS'),
        ('Documentos', 'DOCUMENTOS'),
        ('Procesos', 'PROCESOS'),
        ('Informes', 'INFORMES'),
        ('Seguridad', 'SEGURIDAD'),
    )
    padre = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    codigo = models.CharField(max_length=10, blank=True, null=True)
    url = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    orden = models.CharField(max_length=1024, blank=True, null=True, editable=False)
    ruta = models.CharField(max_length=1024, blank=True, null=True, editable=False)
    clase = models.CharField(max_length=10, blank=True, null=True, choices=CLASE_RECURSO)
    tipo = models.CharField(max_length=15, blank=True, null=True, choices=TIPO_RECURSO)
    icono = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    item_orden = models.IntegerField(default=0, blank=True, null=True)
    habilitado = models.BooleanField(default=False)
    creadopor = models.CharField(max_length=100, blank=True, null=True, editable=False)
    editadopor = models.CharField(max_length=100, blank=True, null=True, editable=False)
    creadodate = models.DateTimeField(auto_now_add=True)
    editadodate = models.DateTimeField(auto_now=True)
    pcid = models.CharField(max_length=200, blank=True, null=True, editable=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return '{} (/{})'.format(self.nombre, self.url)

    class Meta:
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        ordering = ['item_orden']

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.codigo:
            self.codigo = self.codigo.upper()
        try:
            user = get_current_user()

            if self._state.adding:
                self.creadopor = user.username
            else:
                self.editadopor = user.username
        except:
            pass

        super(SegModulo, self).save(force_insert, force_update, using)

        cid = str(self.id).zfill(6)

        if not self.padre is None:
            self.ruta = self.padre.ruta + '/' + cid
            self.orden = self.padre.orden + '/' + str(self.nombre)
        else:
            self.ruta = 'ROOT/' + cid
            self.orden = 'General/' + str(self.nombre)

        super(SegModulo, self).save()

class SegModuloGrupo(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    modulos = models.ManyToManyField(SegModulo)
    grupos = models.ManyToManyField(Group)
    prioridad = models.IntegerField(blank=True, null=True)
    creadopor = models.CharField(max_length=100, blank=True, null=True, editable=False)
    editadopor = models.CharField(max_length=100, blank=True, null=True, editable=False)
    creadodate = models.DateTimeField(auto_now_add=True)
    editadodate = models.DateTimeField(auto_now=True)
    pcid = models.CharField(max_length=200, blank=True, null=True, editable=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return '{} {}'.format(self.nombre, self.prioridad)

    class Meta:
        verbose_name = 'Grupo de Módulos'
        verbose_name_plural = 'Grupos de Módulos'
        ordering = ['prioridad', 'nombre']

    def modulos_activos(self):
        return self.modulos.filter(activo=True).order_by('item_orden')

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()

            if self._state.adding:
                self.creadopor = user.username
            else:
                self.editadopor = user.username
        except:
            pass

        super(SegModuloGrupo, self).save(force_insert, force_update, using)

class SegUsuarioFoto(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.PROTECT)
    foto = models.ImageField(upload_to='usuarios/', verbose_name='Archivo Foto', blank=True, null=True)
    creadopor = models.CharField(max_length=100, blank=True, null=True, editable=False)
    creadodate = models.DateTimeField(auto_now_add=True)
    pcid = models.CharField(max_length=200, blank=True, null=True, editable=False)

    def __str__(self):
        return '{}'.format(self.usuario)

    class Meta:
        verbose_name = 'Usuario Foto'
        verbose_name_plural = 'Usuarios Foto'
        ordering = ['usuario']

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()

            if self._state.adding:
                self.creadopor = user.username
            else:
                self.editadopor = user.username
        except:
            pass

        super(SegUsuarioFoto, self).save(force_insert, force_update, using)

class SegUsuarioParametro(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.PROTECT)
    sucursal = models.ForeignKey(SisSucursales, on_delete=models.PROTECT, blank=True, null=True)
    caja = models.ForeignKey(BanBancos,verbose_name='Factura',on_delete=models.PROTECT,blank=True, null=True,related_name='user_caja_id')
    banco = models.ForeignKey(BanBancos,verbose_name='Cobranza', on_delete=models.PROTECT,blank=True, null=True,related_name='user_banco_id')
    cliente_grupo = models.ForeignKey(CliGrupos,on_delete=models.PROTECT, blank=True, null=True)
    empleado = models.ForeignKey('empleado.EmpEmpleados',on_delete=models.PROTECT, blank=True, null=True)
    inventario = models.ForeignKey('inventario.InvParametroBodegas',on_delete=models.PROTECT, blank=True, null=True)
    creadopor = models.CharField(max_length=100, blank=True, null=True, editable=False)
    creadodate = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    pcid = models.CharField(max_length=200, blank=True, null=True, editable=False)
    activo = models.BooleanField(default=True)
    division = models.ForeignKey('sistema.SisDivisiones', db_column='DivisiónID', on_delete=models.DO_NOTHING,max_length=10, blank=True, null=True, default='')
    codigo_acceso = models.CharField(max_length=50, null=True, blank=True)
    pos_eliminar_item = models.BooleanField(default=False)
    pos_disminuir_cantidad = models.BooleanField(default=False)
    pos_cancelar = models.BooleanField(default=False)
    pos_salir = models.BooleanField(default=False)

    def __str__(self):
        return '{}'.format(self.usuario)

    class Meta:
        verbose_name = 'Usuario Parametro'
        verbose_name_plural = 'Usuario Parametros'
        ordering = ['usuario']

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()

            if self._state.adding:
                self.creadopor = user.username
            else:
                self.editadopor = user.username
        except:
            pass
        super(SegUsuarioParametro, self).save(force_insert, force_update, using)

