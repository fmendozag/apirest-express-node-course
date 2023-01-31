from django.db import models
from django.db.models import Sum, Case, F
from django.db.models.functions import Coalesce

class EmpRubros(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15)  # Field name made lowercase.

    ctadebe = models.ForeignKey('contabilidad.AccCuentas', models.DO_NOTHING, db_column='CtaDebeID',related_name='emp_rubro_debe_id')  # Field name made lowercase.
    ctahaber = models.ForeignKey('contabilidad.AccCuentas', models.DO_NOTHING, db_column='CtaHaberID', blank=True,null=True, related_name='emp_rubro_haber_id')  # Field name made lowercase.

    nombre = models.CharField(db_column='Nombre', max_length=50,blank=True, null=True,default='')  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    liquidación = models.BooleanField(db_column='Liquidación', blank=True, null=True)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True,default='')  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladodate = models.DateTimeField(db_column='AnuladoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True,default='')  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,default='')  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Empleado Rubro'
        verbose_name_plural = 'Empleado Rubros'
        managed = False
        db_table = 'EMP_RUBROS'

class EmpGrupos(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    padre = models.ForeignKey('self', models.DO_NOTHING, db_column='PadreID', blank=True, null=True)  # Field name made lowercase.
    pcid = models.CharField(db_column='PCID', max_length=50, blank=True, null=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    orden = models.CharField(db_column='Orden', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.


    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Grupo empleado'
        verbose_name_plural = 'Grupos empleado'
        managed = False
        db_table = 'EMP_GRUPOS'

class EmpFunciones(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10)  # Field name made lowercase.
    padre = models.ForeignKey('self', models.DO_NOTHING, db_column='PadreID', blank=True, null=True)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True)  # Field name made lowercase.
    pcid = models.CharField(db_column='PCID', max_length=50, blank=True, null=True,default='')  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    sectorial = models.CharField(db_column='Sectorial', max_length=15, blank=True, null=True)  # Field name made lowercase.
    sueldo = models.DecimalField(db_column='Sueldo', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    orden = models.CharField(db_column='Orden', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado')  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Empleado funcion'
        verbose_name_plural = 'Empleado funciones'
        managed = False
        db_table = 'EMP_FUNCIONES'

class EmpTablas(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado')  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Empleado tabla'
        verbose_name_plural = 'Empleado tablas'
        managed = False
        db_table = 'EMP_TABLAS'

class EmpEmpleados(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15)  # Field name made lowercase.
    grupo = models.ForeignKey('EmpGrupos', models.DO_NOTHING, db_column='GrupoID', blank=True, null=True)  # Field name made lowercase.
    zona = models.ForeignKey('sistema.SisZonas', models.DO_NOTHING,db_column='ZonaID', blank=True, null=True)  # Field name made lowercase.
    tabla = models.ForeignKey(EmpTablas, models.DO_NOTHING,db_column='TablaID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    primer_apellido = models.CharField(db_column='PrimerApellido', max_length=20, blank=True, null=True)  # Field name made lowercase.
    segundo_apellido = models.CharField(db_column='SegundoApellido', max_length=20, blank=True, null=True)  # Field name made lowercase.
    primer_nombre = models.CharField(db_column='PrimerNombre', max_length=20, blank=True, null=True)  # Field name made lowercase.
    segundo_nombre = models.CharField(db_column='SegundoNombre', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cedula = models.CharField(db_column='Cédula', max_length=10)  # Field name made lowercase.
    libreta_militar = models.CharField(db_column='LibretaMilitar', max_length=15, blank=True, null=True)  # Field name made lowercase.
    cargo = models.CharField(db_column='Cargo', max_length=40, blank=True, null=True)  # Field name made lowercase.
    iess = models.CharField(db_column='IESS', max_length=10, blank=True, null=True)  # Field name made lowercase.
    direccion = models.CharField(db_column='Dirección', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    telefono1 = models.CharField(db_column='Teléfono1', max_length=20, blank=True, null=True)  # Field name made lowercase.
    telefono2 = models.CharField(db_column='Teléfono2', max_length=20, blank=True, null=True)  # Field name made lowercase.
    telefono3 = models.CharField(db_column='Teléfono3', max_length=20, blank=True, null=True)  # Field name made lowercase.
    sexo = models.CharField(db_column='Sexo', max_length=1, blank=True, null=True)  # Field name made lowercase.
    pastor = models.BooleanField(db_column='Pastor')  # Field name made lowercase.
    tipo_cuenta = models.CharField(db_column='Tipo_Cuenta', max_length=10, blank=True, null=True)  # Field name made lowercase.
    numero_cuenta = models.CharField(db_column='Número_Cuenta', max_length=20, blank=True, null=True)  # Field name made lowercase.
    estado_civil = models.CharField(db_column='EstadoCivil', max_length=15, blank=True, null=True)  # Field name made lowercase.
    fecha_nacimiento = models.DateTimeField(db_column='FechaNac', blank=True, null=True)  # Field name made lowercase.
    fecha_ingreso = models.DateTimeField(db_column='FechaIngreso', blank=True, null=True)  # Field name made lowercase.
    fecha_salida = models.DateTimeField(db_column='FechaSalida', blank=True, null=True)  # Field name made lowercase.
    profesion = models.CharField(db_column='Profesión', max_length=50, blank=True, null=True)  # Field name made lowercase.
    padreid = models.CharField(db_column='PadreID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    sueldo = models.DecimalField(db_column='Sueldo', max_digits=19, decimal_places=4)  # Field name made lowercase.
    sueldo1 = models.DecimalField(db_column='Sueldo1', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    sueldo2 = models.DecimalField(db_column='Sueldo2', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    jornal = models.DecimalField(db_column='Jornal', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    jornalm = models.DecimalField(db_column='JornalM', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    jornalv = models.DecimalField(db_column='JornalV', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    jornaln = models.DecimalField(db_column='JornalN', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    horas = models.DecimalField(db_column='Horas', max_digits=6, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    horasm = models.DecimalField(db_column='HorasM', max_digits=6, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    horasv = models.DecimalField(db_column='HorasV', max_digits=6, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    horasn = models.DecimalField(db_column='HorasN', max_digits=6, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    psueldo = models.DecimalField(db_column='PSueldo', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    psueldo1 = models.DecimalField(db_column='PSueldo1', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    psueldo2 = models.DecimalField(db_column='PSueldo2', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    pjornal = models.DecimalField(db_column='PJornal', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    pjornalm = models.DecimalField(db_column='PJornalM', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    pjornalv = models.DecimalField(db_column='PJornalV', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    pjornaln = models.DecimalField(db_column='PJornalN', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    categoria = models.DecimalField(db_column='Categoría', max_digits=3, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    funcional = models.DecimalField(db_column='Funcional', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    departamentoid = models.CharField(db_column='DepartamentoID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    funcion = models.ForeignKey(EmpFunciones, models.DO_NOTHING,db_column='FunciónID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    cta_comisionid = models.CharField(db_column='CtaComisiónID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tasa_cobertura = models.DecimalField(db_column='TasaCobertura', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    tasa_volumen = models.DecimalField(db_column='TasaVolumen', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    tasa_especial = models.DecimalField(db_column='TasaEspecial', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    orden = models.CharField(db_column='Orden', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=50, blank=True, null=True)  # Field name made lowercase.
    foto = models.CharField(db_column='Foto', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    clase = models.CharField(db_column='Clase', max_length=2, blank=True, null=True)  # Field name made lowercase.
    vendedor = models.BooleanField(db_column='Vendedor', blank=True, null=True)  # Field name made lowercase.
    cobrador = models.BooleanField(db_column='Cobrador', blank=True, null=True)  # Field name made lowercase.
    verificador = models.BooleanField(db_column='Verificador', blank=True, null=True)  # Field name made lowercase.
    entregador = models.BooleanField(db_column='Entregador', blank=True, null=True)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    maternidad = models.BooleanField(db_column='Maternidad')  # Field name made lowercase.
    vacaciones = models.DateTimeField(db_column='Vacaciones', blank=True, null=True)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    calle = models.CharField(db_column='Calle', max_length=20, blank=True, null=True)  # Field name made lowercase.
    divisionid = models.CharField(db_column='DivisiónID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    codigo_reloj = models.CharField(db_column='Código_Reloj', max_length=15, blank=True, null=True)  # Field name made lowercase.
    tip_identificacion = models.CharField(db_column='Tip_Identificacion', max_length=1, blank=True, null=True)  # Field name made lowercase.
    tip_remuneracion = models.CharField(db_column='Tip_Remuneracion', max_length=1, blank=True, null=True)  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10, blank=True, null=True)  # Field name made lowercase.
    cargas_familiares = models.DecimalField(db_column='Cargas_Familiares', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    antiguedad = models.DecimalField(db_column='Antiguedad', max_digits=3, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    siglas = models.CharField(db_column='Siglas', max_length=15, blank=True, null=True)  # Field name made lowercase.
    cod_cliente = models.CharField(db_column='CodCliente', max_length=15, blank=True, null=True)  # Field name made lowercase.
    hora_entrada = models.CharField(db_column='HoraEntrada', max_length=5, blank=True, null=True)  # Field name made lowercase.
    hora_salida = models.CharField(db_column='HoraSalida', max_length=5, blank=True, null=True)  # Field name made lowercase.
    minuto_salmuerzo = models.CharField(db_column='MinutosAlmuerzo', max_length=2, blank=True, null=True)  # Field name made lowercase.
    bonificacion = models.DecimalField(db_column='Bonificación', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    porcentaje = models.DecimalField(db_column='Porcentage', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    decimo13 = models.BooleanField(db_column='Decimo13', blank=True, null=True)  # Field name made lowercase.
    decimo14 = models.BooleanField(db_column='Decimo14', blank=True, null=True)  # Field name made lowercase.
    fondos_reserva = models.BooleanField(db_column='FondosReserva', blank=True, null=True)  # Field name made lowercase.
    bancoid = models.CharField(db_column='BancoID', max_length=10, blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        managed = False
        db_table = 'EMP_EMPLEADOS'

    def get_saldo_total_empleado(self):
        try:
            return self.empempleadosdeudas_set.filter(
                anulado=False,
                credito=False,
                tipo__in=('EMP-FA','EMP-NV')
                ).aggregate(deuda=Coalesce(Sum('saldo'),0))['deuda']
        except:
            return 0

class EmpEmpleadosDeudas(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    empleado = models.ForeignKey('EmpEmpleados', models.DO_NOTHING, db_column='EmpleadoID', blank=True, null=True,default='')  # Field name made lowercase.
    documentoid = models.CharField(db_column='DocumentoID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    asientoid = models.CharField(db_column='AsientoID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    rubro = models.ForeignKey('EmpRubros', models.DO_NOTHING, db_column='RubroID', blank=True, null=True,default='')  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10,editable=False)  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=100,blank=True, null=True,default='')  # Field name made lowercase.
    valor = models.DecimalField(db_column='Valor', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    valor_base = models.DecimalField(db_column='Valor_Base', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha',blank=True, null=True)  # Field name made lowercase.
    vencimiento = models.DateTimeField(db_column='Vencimiento',blank=True, null=True)  # Field name made lowercase.
    ctacxcid = models.ForeignKey('contabilidad.AccCuentas', models.DO_NOTHING, db_column='CtaCxCID', max_length=10, blank=True,null=True, default='')
    divisaid = models.CharField(db_column='DivisaID', max_length=10,blank=True, null=True,default='')  # Field name made lowercase.
    cambio = models.DecimalField(db_column='Cambio', max_digits=12, decimal_places=6,default=0)  # Field name made lowercase.
    saldo = models.DecimalField(db_column='Saldo', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    credito = models.BooleanField(db_column='Crédito',default=False)  # Field name made lowercase.
    deudaid = models.CharField(db_column='DeudaID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    cambiodeuda = models.DecimalField(db_column='CambioDeuda', max_digits=12, decimal_places=6,default=0)  # Field name made lowercase.
    vendedorid = models.CharField(db_column='VendedorID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True,default='')  # Field name made lowercase.
    anuladodate = models.DateTimeField(db_column='AnuladoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladonota = models.CharField(db_column='AnuladoNota', max_length=1024, blank=True, null=True,default='')  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,default='')  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,default='')  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    divisionid = models.CharField(db_column='DivisiónID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    quincena = models.BooleanField(db_column='Quincena', blank=True, null=True,default=False)  # Field name made lowercase.
    secuencia = models.TextField(db_column='Secuencia', blank=True, null=True,default='')  # Field name made lowercase. This field type is a guess.
    ingresoid = models.CharField(db_column='IngresoID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Empleado deuda'
        verbose_name_plural = 'Empleados deudas'
        managed = False
        db_table = 'EMP_EMPLEADOS_DEUDAS'


