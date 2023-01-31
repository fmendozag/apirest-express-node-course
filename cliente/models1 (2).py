from PIL import Image
from crum import get_current_user
from django.db import models
from django.db.models import Case, When, F, Sum
from django.db.models.functions import Coalesce
from django.utils.six import BytesIO
from django.utils.timezone import now

from contadores.fn_contador import get_contador
from inventario.models import InvProductos
from sistema.constantes import LISTA_PRECIOS

class CliRubros(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    ctadebe = models.ForeignKey('contabilidad.AccCuentas',models.DO_NOTHING,db_column='CtaDEBEID',related_name='rubro_debe_id')  # Field name made lowercase.
    ctahaber = models.ForeignKey('contabilidad.AccCuentas',models.DO_NOTHING,db_column='CtaHABERID', blank=True, null=True,related_name='rubro_haber_id')  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=100, blank=True, null=True,default='')  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    impuestoid = models.CharField(db_column='ImpuestoID', max_length=10, blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Cliente Rubro'
        verbose_name_plural = 'Cliente Rubros'
        managed = False
        db_table = 'CLI_RUBROS'

class CliGrupos(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    padre = models.ForeignKey('self',models.DO_NOTHING,db_column='PadreID', blank=True, null=True)  # Field name made lowercase.
    pcid = models.CharField(db_column='PCID', max_length=50, blank=True, null=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15, blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    orden = models.CharField(db_column='Orden', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    aplica_descuentos = models.BooleanField(db_column='AplicaDescuentos', blank=True, null=True)  # Field name made lowercase.
    cuentaid = models.CharField(db_column='CuentaID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    dia_corte = models.DecimalField(db_column='DíaCorte', max_digits=2, decimal_places=0, blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Cliente Grupo'
        verbose_name_plural = 'Cliente Grupos'
        managed = False
        db_table = 'CLI_GRUPOS'

class CliClientes(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', unique=True, max_length=15,editable=False)  # Field name made lowercase.
    grupo = models.ForeignKey('CliGrupos', models.DO_NOTHING, db_column='GrupoID', blank=True, null=True,default='')  # Field name made lowercase.
    zona = models.ForeignKey('sistema.SisZonas',on_delete=models.PROTECT,db_column='ZonaID', blank=True, null=True,default='')  # Field name made lowercase.
    vendedor = models.ForeignKey('empleado.EmpEmpleados', models.DO_NOTHING,db_column='Vendedorid', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    empleadoid = models.CharField(db_column='ClienteID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    clase = models.CharField(db_column='Clase', max_length=2, blank=True, null=True,default='01')  # Field name made lowercase.
    termino = models.CharField(db_column='TérminoID', max_length=10, blank=True, null=True,default='0000000087')  # Field name made lowercase.
    division = models.ForeignKey('sistema.SisDivisiones',models.DO_NOTHING,db_column='DivisiónID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    forma_pago = models.CharField(db_column='FormaPago', max_length=20, blank=True, null=True,default='EFECTIVO')  # Field name made lowercase.
    banco = models.CharField(db_column='Banco', max_length=30, blank=True, null=True,default='(Ninguno)')  # Field name made lowercase.
    cuenta = models.CharField(db_column='Cuenta', max_length=20, blank=True, null=True,default='')  # Field name made lowercase.
    contacto = models.CharField(db_column='Contacto', max_length=60, blank=True, null=True,default='')  # Field name made lowercase.
    tasa_descuento = models.DecimalField(db_column='TasaDescuento', max_digits=6, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    cedula = models.CharField(db_column='Cédula', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    direccion = models.CharField(db_column='Dirección', max_length=100, blank=True, null=True,default='')  # Field name made lowercase.
    telefono1 = models.CharField(db_column='Teléfono1', max_length=20, blank=True, null=True,default='')  # Field name made lowercase.
    telefono2 = models.CharField(db_column='Teléfono2', max_length=20, blank=True, null=True,default='')  # Field name made lowercase.
    telefono3 = models.CharField(db_column='Teléfono3', max_length=20, blank=True, null=True,default='')  # Field name made lowercase.
    telefono4 = models.CharField(db_column='Teléfono4', max_length=20, blank=True, null=True,default='')  # Field name made lowercase.
    ruc = models.CharField(db_column='Ruc', max_length=13, blank=True, null=True)  # Field name made lowercase.
    ciudad = models.CharField(db_column='Ciudad', max_length=40, blank=True, null=True,default='')  # Field name made lowercase.
    cupo = models.DecimalField(db_column='Cupo', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    cupo_factura = models.DecimalField(db_column='CupoFactura', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50, blank=True, null=True)  # Field name made lowercase.
    credito = models.DecimalField(db_column='Crédito', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    #foto = models.CharField(db_column='Foto', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    foto = models.ImageField(upload_to='cliente/%Y/%m/%d/', verbose_name='Archivo foto', blank=True, null=True,db_column='Foto',max_length=1024,default='')
    fecha = models.DateTimeField(db_column='Fecha',auto_now=True, blank=True, null=True)  # Field name made lowercase.
    firma1 = models.CharField(db_column='Firma1', max_length=1024, blank=True, null=True,default='')  # Field name made lowercase.
    firma2 = models.CharField(db_column='Firma2', max_length=1024, blank=True, null=True,default='')  # Field name made lowercase.
    nacimiento = models.DateTimeField(blank=True, null=True)
    email = models.CharField(db_column='Email', max_length=50, blank=True, null=True,default='')  # Field name made lowercase.
    folder = models.CharField(db_column='Folder', max_length=6, blank=True, null=True,default='')  # Field name made lowercase.
    calificacion = models.CharField(db_column='Calificación', max_length=1, blank=True, null=True,default='')  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    www = models.CharField(db_column='WWW', max_length=50, blank=True, null=True,default='')  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate',auto_now_add=True, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate',auto_now=True, blank=True, null=True,editable=False)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True,default='')  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    secuenciaid = models.CharField(db_column='SecuenciaID', max_length=10, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    cuentaid = models.CharField(db_column='CuentaID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    diacorte = models.DecimalField(db_column='DíaCorte', max_digits=5, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    cupones = models.BooleanField(db_column='CUPONES', blank=True, null=True,default=False)  # Field name made lowercase.
    precio_lista = models.BooleanField(db_column='PrecioLista',default=False)  # Field name made lowercase.
    fecha_credito = models.DateTimeField(db_column='FechaCrédito',auto_now=True, blank=True, null=True)  # Field name made lowercase.
    tasa_incremento = models.DecimalField(db_column='TasaIncremento', max_digits=6, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    relacionado = models.BooleanField(db_column='Relacionado',default=False)  # Field name made lowercase.
    precio_activo = models.DecimalField(db_column='PrecioActivo', max_digits=1,choices=LISTA_PRECIOS,decimal_places=0, blank=True, null=True,default=1)  # Field name made lowercase.
    cobrador = models.CharField(db_column='CobradorID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    clase_ruc = models.DecimalField(db_column='ClaseRuc', max_digits=1, decimal_places=0, blank=True, null=True,default=2)  # Field name made lowercase.
    gps_latitud = models.CharField(db_column='gps_latitud',max_length=50, blank=True, null=True,default='')
    gps_longitud = models.CharField(db_column='gps_longitud',max_length=50, blank=True, null=True,default='')
    referencia = models.CharField(db_column='referencia',max_length=100, blank=True, null=True,default='')
    dia_visita = models.CharField(db_column='dia_visita',max_length=1, blank=True, null=True,default='')
    dia_entrega = models.CharField(db_column='dia_entrega',max_length=1, blank=True, null=True,default='')
    nombre_comercial = models.CharField(db_column='NombreComercial',max_length=100, blank=True, null=True,default='')

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        managed = False
        db_table = 'CLI_CLIENTES'

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.nombre:
            self.nombre = self.nombre.strip().upper()

        if self.direccion:
            self.direccion = self.direccion.strip().upper()

        if self.email:
            self.email = self.email.strip().lower()
        else:
            self.email = ''
        try:
            user = get_current_user()
            if self._state.adding:
                self.id = get_contador('CLI_CLIENTES-ID', user)
                self.sucursalid = user.segusuarioparametro.banco.sucursal
                self.creadopor = user.username
            else:
                self.editadopor = user.username
        except:
            pass

        if self.foto:
            try:
                image_file = BytesIO(self.foto.file.read())
                image = Image.open(image_file)
                image.thumbnail((600, 600), Image.ANTIALIAS)
                image_file = BytesIO()
                image.save(image_file, 'PNG')
                self.foto.file = image_file
                self.foto.image = image
            except IOError:
                pass

        super(CliClientes, self).save(force_insert, force_update, using)
        try:
            self.codigo = '{}-{}-{}'.format(self.sucursalid,self.ciudad[0:2].upper(),self.id[-9:])
        except:
            try:
                self.codigo = '{}'.format(int(self.id))
            except:
                pass
        super(CliClientes, self).save()

    def get_foto(self):
        try:
            return str(self.foto.url)
        except:
            pass
        return None

    def get_validar_ruc(self):
        return CliClientes.objects.filter(anulado=False,ruc=self.ruc).exclude(id=self.id).exists()

    def get_saldo_total(self):
        try:
            return self.cliclientesdeudas_set.filter(
                anulado=False,
                saldo__gt=0
                ).aggregate(
                saldo_total=Coalesce(Sum(
                    Case(
                        When(credito=True, then=-F('saldo')),
                        default=F('saldo')
                        )
                ),0))['saldo_total']
        except:
            return 0

class CliClientesDeudas(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    cliente = models.ForeignKey('CliClientes', models.DO_NOTHING, db_column='ClienteID')  # Field name made lowercase.
    documentoid = models.CharField(db_column='DocumentoID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    asientoid = models.CharField(db_column='AsientoID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10, blank=True, null=True,editable=False)  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=100,blank=True, null=True,default='')  # Field name made lowercase.
    valor = models.DecimalField(db_column='Valor', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    valor_base = models.DecimalField(db_column='ValorBase', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha',blank=True, null=True)  # Field name made lowercase.
    vencimiento = models.DateTimeField(db_column='Vencimiento',blank=True, null=True)  # Field name made lowercase.
    rubro = models.ForeignKey(CliRubros, models.DO_NOTHING,db_column='RubroID', max_length=10,blank=True, null=True,default='')  # Field name made lowercase.
    cta_cxcobrar = models.ForeignKey('contabilidad.AccCuentas',models.DO_NOTHING,db_column='CtaCxCID', max_length=10,blank=True, null=True,default='')  # Field name made lowercase.
    divisaid = models.CharField(db_column='DivisaID', max_length=10,blank=True, null=True,default='')  # Field name made lowercase.
    cambio = models.DecimalField(db_column='Cambio', max_digits=12, decimal_places=6,default=0)  # Field name made lowercase.
    saldo = models.DecimalField(db_column='Saldo', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10,blank=True, null=True,default='')  # Field name made lowercase.
    credito = models.BooleanField(db_column='Crédito',default=False)  # Field name made lowercase.
    facturado = models.BooleanField(db_column='Facturado',default=False)  # Field name made lowercase.
    deudaid = models.CharField(db_column='DeudaID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    cambio_deuda = models.DecimalField(db_column='CambioDeuda', max_digits=12, decimal_places=6, blank=True, null=True)  # Field name made lowercase.
    vendedorid = models.CharField(db_column='VendedorID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladodate = models.DateTimeField(db_column='AnuladoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladonota = models.CharField(db_column='AnuladoNota', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,editable=False)  # Field name made lowercase.
    divisionid = models.CharField(db_column='DivisiónID', max_length=10, blank=True, null=True,editable=False)  # Field name made lowercase.
    secuencia = models.TextField(db_column='Secuencia', blank=True, null=True,editable=False)  # Field name made lowercase. This field type is a guess.
    facturaid = models.CharField(db_column='FacturaID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    numcartilla = models.CharField(db_column='NumCartilla', max_length=15, blank=True, null=True)  # Field name made lowercase.
    retenido = models.BooleanField(db_column='Retenido', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.fecha)

    class Meta:
        verbose_name = 'Cliente Deuda'
        verbose_name_plural = 'Cliente Deudas'
        managed = False
        db_table = 'CLI_CLIENTES_DEUDAS'

class CliCotizaciones(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10,editable=False)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10,default='COT-FA')  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha',default=now)  # Field name made lowercase.
    cliente = models.ForeignKey(CliClientes, models.DO_NOTHING, db_column='ClienteID',max_length=10,default='')  # Field name made lowercase.
    nombre = models.CharField(db_column='Cliente', max_length=50,blank=True, null=True,default='')  # Field name made lowercase.
    vendedor = models.ForeignKey('empleado.EmpEmpleados',models.DO_NOTHING,db_column='VendedorID', max_length=10,blank=True, null=True,default='')  # Field name made lowercase.
    divisaid = models.CharField(db_column='DivisaID', max_length=10,blank=True, null=True,default='')  # Field name made lowercase.
    cambio = models.DecimalField(db_column='Cambio', max_digits=12, decimal_places=6,default=1)  # Field name made lowercase.
    atentamente = models.CharField(db_column='Atentamente', max_length=60,blank=True, null=True,default='')  # Field name made lowercase.
    validez = models.CharField(db_column='Validez', max_length=30,blank=True, null=True,default='')  # Field name made lowercase.
    terminoid = models.CharField(db_column='TérminoID', max_length=10,blank=True, null=True,default='')  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=100,blank=True, null=True,default='')  # Field name made lowercase.
    division = models.CharField(db_column='DivisiónID', max_length=10,blank=True, null=True,default='')  # Field name made lowercase.
    subtotal = models.DecimalField(db_column='SubTotal', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    descuento = models.DecimalField(db_column='Descuento', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    impuesto = models.DecimalField(db_column='Impuesto', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    total = models.DecimalField(db_column='Total', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024,blank=True, null=True,default='')  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(auto_now_add=True,db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(auto_now=True,db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    anuladodate = models.DateTimeField(db_column='AnuladoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladonota = models.CharField(db_column='AnuladoNota', max_length=1024, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    caja = models.ForeignKey('banco.BanBancos', models.DO_NOTHING, db_column='CajaID', max_length=10, blank=True,null=True,default='')
    caja_code = models.CharField(db_column='CajaCode', max_length=15, blank=True, null=True,default='')  # Field name made lowercase.
    contado = models.BooleanField(db_column='Contado', default=False)  # Field name made lowercase.
    empleadoid = models.CharField(db_column='EmpleadoID', max_length=10, blank=True,null=True,default='')  # Field name made lowercase.
    bodega = models.ForeignKey('inventario.InvBodegas', models.DO_NOTHING, db_column='BodegaID', max_length=10,blank=True, null=True,default='')  # Field name made lowercase.
    entregado = models.DateTimeField(db_column='Entregado', blank=True, null=True)  # Field name made lowercase.
    subtotalcero = models.DecimalField(db_column='SubTotalCero', max_digits=19, decimal_places=4, blank=True,null=True,default=0)  # Field name made lowercase.
    subtotaliva = models.DecimalField(db_column='SubTotalIVA', max_digits=19, decimal_places=4, blank=True,null=True,default=0)  # Field name made lowercase.
    descuentocero = models.DecimalField(db_column='DescuentoCero', max_digits=19, decimal_places=4, blank=True,null=True,default=0)  # Field name made lowercase.
    descuentoiva = models.DecimalField(db_column='DescuentoIVA', max_digits=19, decimal_places=4, blank=True,null=True,default=0)  # Field name made lowercase.
    totalcomision = models.DecimalField(db_column='TotalComision', max_digits=19, decimal_places=4, blank=True,null=True,default=0)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.numero)

    class Meta:
        verbose_name = 'Clientes Cotizacion'
        verbose_name_plural = 'Clientes Cotizaciones'
        managed = False
        db_table = 'CLI_COTIZACIONES'

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
            else:
                self.editadopor = user.username
        except:
            pass
        super(CliCotizaciones, self).save(force_insert, force_update, using)

class CliCotizacionesDetalle(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    cotizacion = models.ForeignKey('CliCotizaciones', models.DO_NOTHING, db_column='CotizaciónID')  # Field name made lowercase.
    producto = models.ForeignKey(InvProductos, models.DO_NOTHING, db_column='ProductoID')  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50, blank=True, null=True,default='')  # Field name made lowercase.
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=11, decimal_places=2,default=0)  # Field name made lowercase.
    old_cantidad = models.DecimalField(db_column='oldCantidad', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    precio = models.DecimalField(db_column='Precio', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    subtotal = models.DecimalField(db_column='Subtotal', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    tasa_descuento = models.DecimalField(db_column='TasaDescuento', max_digits=5, decimal_places=2,default=0)  # Field name made lowercase.
    descuento = models.DecimalField(db_column='Descuento', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    tasa_impuesto = models.DecimalField(db_column='TasaImpuesto', max_digits=5, decimal_places=2,default=0)  # Field name made lowercase.
    impuesto = models.DecimalField(db_column='Impuesto', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    total = models.DecimalField(db_column='Total', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    clase = models.CharField(db_column='Clase', max_length=2, blank=True, null=True,default='')  # Field name made lowercase.
    empaque = models.CharField(db_column='Empaque', max_length=40, blank=True, null=True,default='')  # Field name made lowercase.
    embarque = models.BooleanField(db_column='Embarque',default=False)  # Field name made lowercase.
    detalle_ex = models.CharField(db_column='Detalle_ex', max_length=1024, blank=True, null=True,default='')  # Field name made lowercase.
    precio_name = models.CharField(db_column='PrecioName', max_length=40, blank=True, null=True,default='')  # Field name made lowercase.
    factor = models.DecimalField(db_column='Factor', max_digits=6, decimal_places=2,default=0)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate',auto_now_add=True,blank=True, null=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,default='')  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado', default=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor',max_length=50,blank=True,null=True)  # Field name made lowercase.
    bodegaid = models.CharField(db_column='BodegaID', max_length=10, blank=True,null=True,default='')  # Field name made lowercase.
    codigo = models.CharField(db_column='Codigo', max_length=20, blank=True, null=True,default='')  # Field name made lowercase.
    precio_display = models.DecimalField(db_column='PrecioDisplay', max_digits=19, decimal_places=4, blank=True,null=True,default=0)  # Field name made lowercase.
    precio_factor = models.DecimalField(db_column='PrecioFactor', max_digits=19, decimal_places=4, blank=True,null=True,default=0)  # Field name made lowercase.
    precio_final = models.DecimalField(db_column='PrecioFinal', max_digits=19, decimal_places=4, blank=True,null=True,default=0)  # Field name made lowercase.
    costo = models.DecimalField(db_column='Costo', max_digits=19, decimal_places=4, blank=True,null=True,default=0)  # Field name made lowercase.
    impuestoid = models.CharField(db_column='ImpuestoID', max_length=10, blank=True,null=True,default='')  # Field name made lowercase.
    coniva = models.BooleanField(db_column='ConIva',default=False)  # Field name made lowercase.
    valor_comision = models.DecimalField(db_column='ValorComision', max_digits=19, decimal_places=4, blank=True,null=True,default=0)  # Field name made lowercase.
    comision_contado = models.DecimalField(db_column='ComisionContado', max_digits=19, decimal_places=4, blank=True,null=True,default=0)  # Field name made lowercase.
    comision_credito = models.DecimalField(db_column='ComisionCredito', max_digits=19, decimal_places=4, blank=True,null=True,default=0)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.cotizacion.numero)

    class Meta:
        verbose_name = 'Clientes Cotizacion Detalle'
        verbose_name_plural = 'Clientes Cotizaciones Detalles'
        managed = False
        db_table = 'CLI_COTIZACIONES_DT'


    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
        except:
            pass
        super(CliCotizacionesDetalle, self).save(force_insert, force_update, using)
