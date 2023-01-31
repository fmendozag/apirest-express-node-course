from crum import get_current_user
from django.db import models
from django.db.models import Sum, Count, F
from django.db.models.functions import Coalesce
from django.http import Http404
from contadores.fn_contador import get_contador_sucdiv
from sistema.constantes import ESTADO_TRANSFERENCIA, INV_ESTADO_CONTEO

class InvBodegas(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10, editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    responsable = models.CharField(db_column='Responsable', max_length=50, blank=True,
                                   null=True)  # Field name made lowercase.
    direccion = models.CharField(db_column='Dirección', max_length=50, blank=True,
                                 null=True)  # Field name made lowercase.
    telefonos = models.CharField(db_column='Teléfonos', max_length=20, blank=True,
                                 null=True)  # Field name made lowercase.
    sucursal = models.CharField(db_column='Sucursal', max_length=2)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    venta = models.BooleanField(db_column='Venta')  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado', default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,
                                 editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,
                                      editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,
                                       editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,
                            editable=False)  # Field name made lowercase.
    transferencia = models.BooleanField(db_column='Transferencia', default=False)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        managed = False
        db_table = 'INV_BODEGAS'

class InvGrupos(models.Model):
    TIPO_GRUPO = (
        ('GRUPO', 'GRUPO'),
        ('ITEM', 'ITEM'),
    )
    MODELO_TIPO = (
        (1, 'COBERTURA'),
        (2, 'MAYORISTA'),
    )

    id = models.CharField(db_column='ID', primary_key=True, max_length=10, editable=False)  # Field name made lowercase.
    padre = models.ForeignKey('self', models.DO_NOTHING, db_column='PadreID', blank=True, null=True, default='')
    codigo = models.CharField(db_column='Código', unique=True, max_length=15)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50, default='')  # Field name made lowercase.

    # modelo_tipo = models.IntegerField(choices=MODELO_TIPO,db_column='ModeloTipo', blank=True, null=True,verbose_name='Modelo',default='')
    # rentabilidad_costo_contado = models.DecimalField(db_column='RentabilidadCostoContado', max_digits=5, decimal_places=2, blank=True, null=True,verbose_name='Rent.Contado',default=0)
    # rentabilidad_costo_credito = models.DecimalField(db_column='RentabilidadCostoCredito', max_digits=5, decimal_places=2, blank=True, null=True,verbose_name='Rent.Credito',default=0)
    #
    # comision_pvp_contado = models.DecimalField(db_column='ComisionPvpContado', max_digits=5, decimal_places=2, blank=True, null=True,verbose_name='Comision Contado',default=0)
    # comision_pvp_credito = models.DecimalField(db_column='ComisionPvpCredito', max_digits=5, decimal_places=2, blank=True, null=True,verbose_name='Comision Credito',default=0)

    orden = models.CharField(db_column='Orden', max_length=1024, blank=True, null=True, editable=False,
                             default='')  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=1024, blank=True, null=True, editable=False,
                            default='')  # Field name made lowercase.
    tipo = models.CharField(choices=TIPO_GRUPO, db_column='Tipo', max_length=10, blank=True, null=True,
                            default='')  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado', default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True, editable=False,
                                 default='')  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,
                                      editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,
                                       editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True, editable=False,
                            default='')  # Field name made lowercase.
    surtido = models.BooleanField(db_column='Surtido', blank=True, null=True,
                                  default=False)  # Field name made lowercase.
    desc_lunes = models.BooleanField(db_column='DescLunes', blank=True, null=True, editable=False,
                                     default=False)  # Field name made lowercase.
    desc_martes = models.BooleanField(db_column='DescMartes', blank=True, null=True, editable=False,
                                      default=False)  # Field name made lowercase.
    desc_miercoles = models.BooleanField(db_column='DescMiércoles', blank=True, null=True, editable=False,
                                         default=False)  # Field name made lowercase.
    desc_jueves = models.BooleanField(db_column='DescJueves', blank=True, null=True, editable=False,
                                      default=False)  # Field name made lowercase.
    desc_viernes = models.BooleanField(db_column='DescViernes', blank=True, null=True, editable=False,
                                       default=False)  # Field name made lowercase.
    desc_sabado = models.BooleanField(db_column='DescSábado', blank=True, null=True, editable=False,
                                      default=False)  # Field name made lowercase.
    desc_domingo = models.BooleanField(db_column='DescDomingo', blank=True, null=True, editable=False,
                                       default=False)  # Field name made lowercase.
    tasa_lunes = models.DecimalField(db_column='TasaLunes', max_digits=5, decimal_places=2, blank=True, null=True,
                                     editable=False, default=0)  # Field name made lowercase.
    tasa_martes = models.DecimalField(db_column='TasaMartes', max_digits=5, decimal_places=2, blank=True, null=True,
                                      editable=False, default=0)  # Field name made lowercase.
    tasa_miercoles = models.DecimalField(db_column='TasaMiércoles', max_digits=5, decimal_places=2, blank=True,
                                         null=True, editable=False, default=0)  # Field name made lowercase.
    tasa_jueves = models.DecimalField(db_column='TasaJueves', max_digits=5, decimal_places=2, blank=True, null=True,
                                      editable=False, default=0)  # Field name made lowercase.
    tasa_viernes = models.DecimalField(db_column='TasaViernes', max_digits=5, decimal_places=2, blank=True, null=True,
                                       editable=False, default=0)  # Field name made lowercase.
    tasa_sabado = models.DecimalField(db_column='TasaSábado', max_digits=5, decimal_places=2, blank=True, null=True,
                                      editable=False, default=0)  # Field name made lowercase.
    tasa_domingo = models.DecimalField(db_column='TasaDomingo', max_digits=5, decimal_places=2, blank=True, null=True,
                                       editable=False, default=0)  # Field name made lowercase.
    cupon = models.DecimalField(db_column='cupón', max_digits=19, decimal_places=4, blank=True, null=True, default=0,
                                editable=False)
    aplica_cupon = models.BooleanField(db_column='AplicaCupón', blank=True, null=True, default=False,
                                       editable=False)  # Field name made lowercase.
    minimo_unidades = models.DecimalField(db_column='MínimoUnidades', max_digits=11, decimal_places=2, blank=True,
                                          null=True, editable=False, default=0)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        managed = False
        db_table = 'INV_GRUPOS'

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
            else:
                self.editadopor = user.username
                # self.set_update_porcentaje_comision()
        except:
            pass
        super(InvGrupos, self).save(force_insert, force_update, using)

class InvParametroBodegas(models.Model):
    TIPO_PARAMETRO = (
        ('1', 'TRANFERENCIA'),
    )
    grupo = models.ForeignKey('banco.BanGrupos', max_length=10, blank=True, null=True,
                              on_delete=models.PROTECT)  # Field name made lowercase.
    sucursal = models.ForeignKey('sistema.SisSucursales', on_delete=models.PROTECT, blank=True, null=True)
    division = models.ForeignKey('sistema.SisDivisiones', on_delete=models.PROTECT, max_length=10, blank=True,
                                 null=True)
    bodega = models.ForeignKey(InvBodegas, on_delete=models.PROTECT, max_length=10, blank=True,
                               null=True)  # Field name made lowercase.
    tipo = models.CharField(max_length=2, choices=TIPO_PARAMETRO, blank=True, null=True, default='1')
    serie = models.CharField(max_length=7, blank=True, null=True, default='')  # Field name made lowercase.
    codigo = models.CharField(max_length=15, blank=True, null=True, default='')  # Field name made lowercase.
    nombre = models.CharField(max_length=50, blank=True, null=True, default='')  # Field name made lowercase.
    clase = models.CharField(max_length=2, blank=True, null=True,
                             choices=(('01', '01'), ('02', '02')))  # Field name made lowercase.
    divisaid = models.CharField(max_length=10, blank=True, null=True,
                                default='0000000001')  # Field name made lowercase.
    nota = models.CharField(max_length=1024, blank=True, null=True, default='')  # Field name made lowercase.
    anulado = models.BooleanField(default=False)
    creadopor = models.CharField(max_length=15, blank=True, null=True, editable=False)  # Field name made lowercase.
    editadopor = models.CharField(max_length=15, blank=True, null=True, editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(auto_now_add=True, blank=True, null=True,
                                      editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(auto_now=True, blank=True, null=True,
                                       editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(max_length=2, blank=True, null=True, editable=False)  # Field name made lowercase.
    pcid = models.CharField(max_length=50, blank=True, null=True, editable=False,
                            default='')  # Field name made lowercase.
    anuladopor = models.CharField(max_length=15, blank=True, null=True, editable=False,
                                  default='')  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Parametro Bodega'
        verbose_name_plural = 'Parametros Bodegas'

class InvProductos(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10, editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=20, default='')  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    nombre_corto = models.CharField(db_column='NombreCorto', max_length=30, blank=True, null=True,
                                    default='')  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripción', max_length=50, blank=True, null=True,
                                   default='')  # Field name made lowercase.
    enlace = models.CharField(db_column='Enlace', max_length=20, blank=True, null=True,
                              default='')  # Field name made lowercase.
    clase = models.CharField(db_column='Clase', max_length=2, blank=True, null=True,
                             default='')  # Field name made lowercase.
    grupo = models.ForeignKey('InvGrupos', models.DO_NOTHING, db_column='GrupoID', blank=True, null=True,
                              default='')  # Field name made lowercase.
    proveedor = models.ForeignKey('acreedor.AcrAcreedores', models.DO_NOTHING, db_column='ProveedorID', blank=True,
                                  null=True, default='')  # Field name made lowercase.
    ctamayor = models.ForeignKey('contabilidad.AccCuentas', models.DO_NOTHING, db_column='CtaMayorID', max_length=10,
                                 blank=True, null=True, related_name='cta_prod_mayor_id',
                                 default='')  # Field name made lowercase.
    ctaventas = models.ForeignKey('contabilidad.AccCuentas', models.DO_NOTHING, db_column='CtaVentasID', max_length=10,
                                  blank=True, null=True, related_name='cta_prod_venta_id',
                                  default='')  # Field name made lowercase.
    ctacostos = models.ForeignKey('contabilidad.AccCuentas', models.DO_NOTHING, db_column='CtaCostosID', max_length=10,
                                  blank=True, null=True, related_name='cta_prod_costo_id',
                                  default='')  # Field name made lowercase.
    ctadescuento = models.ForeignKey('contabilidad.AccCuentas', models.DO_NOTHING, db_column='CtaDescuentoID',
                                     max_length=10, blank=True, null=True, related_name='cta_prod_descuento_id',
                                     default='')  # Field name made lowercase.
    ctadevolucion = models.ForeignKey('contabilidad.AccCuentas', models.DO_NOTHING, db_column='CtaDevoluciónID',
                                      max_length=10, blank=True, null=True, related_name='cta_prod_devolucion_id',
                                      default='')  # Field name made lowercase.
    cta_retencion = models.ForeignKey('contabilidad.AccCuentas', models.DO_NOTHING, db_column='CtaRetenciónID',
                                      max_length=10, blank=True, null=True, related_name='cta_prod_retencion_id',
                                      default='')  # Field name made lowercase.
    marca = models.CharField(db_column='Marca', max_length=30, blank=True, null=True,
                             default='')  # Field name made lowercase.
    color = models.CharField(db_column='Color', max_length=30, blank=True, null=True,
                             default='')  # Field name made lowercase.
    ubicacion = models.CharField(db_column='Ubicación', max_length=50, blank=True, null=True,
                                 default='')  # Field name made lowercase.
    peso = models.DecimalField(db_column='Peso', max_digits=6, decimal_places=2, blank=True, null=True,
                               default=0)  # Field name made lowercase.
    modelo = models.CharField(db_column='Modelo', max_length=50, blank=True, null=True,
                              default='')  # Field name made lowercase.
    procedencia = models.CharField(db_column='Procedencia', max_length=50, blank=True, null=True,
                                   default='')  # Field name made lowercase.
    stock_maximo = models.DecimalField(db_column='StockMáximo', max_digits=6, decimal_places=0, blank=True, null=True,
                                       default=0)  # Field name made lowercase.
    stock_minimo = models.DecimalField(db_column='StockMínimo', max_digits=6, decimal_places=0, blank=True, null=True,
                                       default=0)  # Field name made lowercase.
    peso_maximo = models.DecimalField(db_column='PesoMáximo', max_digits=10, decimal_places=2, blank=True, null=True,
                                      default=0)  # Field name made lowercase.
    peso_minimo = models.DecimalField(db_column='PesoMínimo', max_digits=10, decimal_places=2, blank=True, null=True,
                                      default=0)  # Field name made lowercase.
    tecla = models.CharField(db_column='Tecla', max_length=2, blank=True, null=True,
                             default='')  # Field name made lowercase.
    entrega = models.DecimalField(db_column='Entrega', max_digits=6, decimal_places=0, blank=True, null=True,
                                  default=0)  # Field name made lowercase.
    metodo = models.CharField(db_column='Método', max_length=10, blank=True, null=True,
                              default='')  # Field name made lowercase.
    impuestoid = models.CharField(db_column='ImpuestoID', max_length=10, blank=True, null=True,
                                  default='')  # Field name made lowercase.
    impuesto_compraid = models.CharField(db_column='ImpuestoCompraID', max_length=10, blank=True, null=True,
                                         default='')  # Field name made lowercase.
    empaque = models.CharField(db_column='Empaque', max_length=10, blank=True, null=True,
                               default='')  # Field name made lowercase.
    medida = models.DecimalField(db_column='Medida', max_digits=6, decimal_places=2, blank=True, null=True,
                                 default=0)  # Field name made lowercase.
    costo_promedio = models.DecimalField(db_column='CostoPromedio', max_digits=19, decimal_places=4, blank=True,
                                         null=True, default=0)  # Field name made lowercase.
    costo_lista = models.DecimalField(db_column='CostoLista', max_digits=19, decimal_places=4, blank=True,
                                      null=True)  # Field name made lowercase.
    costo_compra = models.DecimalField(db_column='CostoCompra', max_digits=19, decimal_places=4, blank=True, null=True,
                                       default=0)  # Field name made lowercase.
    costo_rp = models.DecimalField(db_column='CostoRp', max_digits=19, decimal_places=4, blank=True, null=True,
                                   default=0)  # Field name made lowercase.
    precio1 = models.DecimalField(db_column='Precio1', max_digits=19, decimal_places=4, blank=True, null=True,
                                  default=0)  # Field name made lowercase.
    precio2 = models.DecimalField(db_column='Precio2', max_digits=19, decimal_places=4, blank=True, null=True,
                                  default=0)  # Field name made lowercase.
    precio3 = models.DecimalField(db_column='Precio3', max_digits=19, decimal_places=4, blank=True, null=True,
                                  default=0)  # Field name made lowercase.
    precio4 = models.DecimalField(db_column='Precio4', max_digits=19, decimal_places=4, blank=True, null=True,
                                  default=0)  # Field name made lowercase.
    precio5 = models.DecimalField(db_column='Precio5', max_digits=19, decimal_places=4, blank=True, null=True,
                                  default=0)  # Field name made lowercase.
    precio6 = models.DecimalField(db_column='Precio6', max_digits=19, decimal_places=4, blank=True, null=True,
                                  default=0)  # Field name made lowercase.
    precio7 = models.DecimalField(db_column='Precio7', max_digits=19, decimal_places=4, blank=True, null=True,
                                  default=0)  # Field name made lowercase.
    promocion = models.DecimalField(db_column='Promoción', max_digits=19, decimal_places=4, blank=True, null=True,
                                    default=0)  # Field name made lowercase.
    conversion = models.DecimalField(db_column='Conversión', max_digits=7, decimal_places=2, blank=True, null=True,
                                     default=0)  # Field name made lowercase.
    comision = models.BooleanField(db_column='Comisión', default=False)  # Field name made lowercase.
    formula = models.CharField(db_column='Formula', max_length=80, blank=True, null=True,
                               default='')  # Field name made lowercase.
    comision1 = models.DecimalField(db_column='Comisión1', max_digits=19, decimal_places=4, blank=True, null=True,
                                    default=0)  # Field name made lowercase.
    comision2 = models.DecimalField(db_column='Comisión2', max_digits=19, decimal_places=4, blank=True, null=True,
                                    default=0)  # Field name made lowercase.
    comision3 = models.DecimalField(db_column='Comisión3', max_digits=19, decimal_places=4, blank=True, null=True,
                                    default=0)  # Field name made lowercase.
    comision4 = models.DecimalField(db_column='Comisión4', max_digits=19, decimal_places=4, blank=True, null=True,
                                    default=0)  # Field name made lowercase.
    comision5 = models.DecimalField(db_column='Comisión5', max_digits=19, decimal_places=4, blank=True, null=True,
                                    default=0)  # Field name made lowercase.
    comision6 = models.DecimalField(db_column='Comisión6', max_digits=19, decimal_places=4, blank=True, null=True,
                                    default=0)  # Field name made lowercase.
    tasa_utilidad_min = models.DecimalField(db_column='TasaUtilidadMin', max_digits=5, decimal_places=2, blank=True,
                                            null=True, default=0)  # Field name made lowercase.
    tasa_utilidad_max = models.DecimalField(db_column='TasaUtilidadMax', max_digits=5, decimal_places=2, blank=True,
                                            null=True, default=0)  # Field name made lowercase.
    foto = models.ImageField(upload_to='productos/', db_column='Foto', verbose_name='Archivo foto', max_length=1024,
                             blank=True, null=True, default='')
    vendible = models.BooleanField(db_column='Vendible', blank=True, null=True,
                                   default=True)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado', default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True, editable=False,
                                 default='')  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,
                                      editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,
                                       editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,
                                  editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True, editable=False,
                            default='')  # Field name made lowercase.
    unidades_prom = models.DecimalField(db_column='UnidadesProm', max_digits=5, decimal_places=0, blank=True, null=True,
                                        default=0)  # Field name made lowercase.
    factor_prom = models.DecimalField(db_column='FactorProm', max_digits=5, decimal_places=0, blank=True, null=True,
                                      default=0)  # Field name made lowercase.
    promocionid = models.CharField(db_column='PromociónID', max_length=10, blank=True, null=True,
                                   default='')  # Field name made lowercase.
    ctamermaid = models.CharField(db_column='CtaMermaID', max_length=10, blank=True, null=True,
                                  default='')  # Field name made lowercase.
    merma = models.DecimalField(db_column='Merma', max_digits=5, decimal_places=2, blank=True, null=True,
                                default=0)  # Field name made lowercase.
    peso_unidades = models.BooleanField(db_column='PesoUnidades', blank=True, null=True,
                                        default=False)  # Field name made lowercase.
    minimo_unidades = models.DecimalField(db_column='MínimoUnidades', max_digits=11, decimal_places=2, blank=True,
                                          null=True, default=0)  # Field name made lowercase.
    cupon = models.DecimalField(db_column='Cupón', max_digits=19, decimal_places=4, blank=True, null=True,
                                default=0)  # Field name made lowercase.
    aplica_cupon = models.BooleanField(db_column='AplicaCupón', blank=True, null=True)  # Field name made lowercase.
    balanzz = models.BooleanField(db_column='Balanzz', blank=True, null=True)  # Field name made lowercase.
    balanza = models.BooleanField(db_column='Balanza', blank=True, null=True)  # Field name made lowercase.
    fecha_compra = models.DateTimeField(db_column='FechaCompra', blank=True, null=True)  # Field name made lowercase.
    costo_temporal = models.DecimalField(db_column='CostoTemporal', max_digits=19, decimal_places=4, blank=True,
                                         null=True)  # Field name made lowercase.
    gana_club = models.BooleanField(db_column='GanaClub', blank=True, null=True)  # Field name made lowercase.
    valor_ganaclub = models.DecimalField(db_column='ValorGanaClub', max_digits=19, decimal_places=4, blank=True,
                                         null=True)  # Field name made lowercase.
    valor_ganaclub1 = models.DecimalField(db_column='ValorGanaClub1', max_digits=19, decimal_places=4, blank=True,
                                          null=True)  # Field name made lowercase.
    valor_ganaclub2 = models.DecimalField(db_column='ValorGanaClub2', max_digits=19, decimal_places=4, blank=True,
                                          null=True)  # Field name made lowercase.
    valor_ganaclub3 = models.DecimalField(db_column='ValorGanaClub3', max_digits=19, decimal_places=4, blank=True,
                                          null=True)  # Field name made lowercase.
    cupon1 = models.DecimalField(db_column='Cupón1', max_digits=19, decimal_places=4, blank=True,
                                 null=True)  # Field name made lowercase.
    cupon2 = models.DecimalField(db_column='Cupón2', max_digits=19, decimal_places=4, blank=True,
                                 null=True)  # Field name made lowercase.
    cupon3 = models.DecimalField(db_column='Cupón3', max_digits=19, decimal_places=4, blank=True,
                                 null=True)  # Field name made lowercase.
    cupon4 = models.DecimalField(db_column='Cupón4', max_digits=19, decimal_places=4, blank=True,
                                 null=True)  # Field name made lowercase.
    aplica_cupon_supermercado = models.BooleanField(db_column='AplicaCupónSupermercado', blank=True,
                                                    null=True)  # Field name made lowercase.
    precio8 = models.DecimalField(db_column='Precio8', max_digits=19, decimal_places=4, blank=True,
                                  null=True)  # Field name made lowercase.
    precio9 = models.DecimalField(db_column='Precio9', max_digits=19, decimal_places=4, blank=True,
                                  null=True)  # Field name made lowercase.
    precio10 = models.DecimalField(db_column='Precio10', max_digits=19, decimal_places=4, blank=True,
                                   null=True)  # Field name made lowercase.
    codigo_barra1 = models.CharField(db_column='CódigoBarra1', max_length=20, blank=True,
                                     null=True)  # Field name made lowercase.
    codigo_barra2 = models.CharField(db_column='CódigoBarra2', max_length=20, blank=True,
                                     null=True)  # Field name made lowercase.
    fecha_precio = models.DateTimeField(db_column='FechaPrecio', blank=True, null=True)  # Field name made lowercase.
    ptg_descuento = models.DecimalField(db_column='PtgDescuento', max_digits=6, decimal_places=2, blank=True,
                                        null=True)  # Field name made lowercase.
    cantidad1 = models.DecimalField(db_column='Cantidad1', max_digits=6, decimal_places=2, blank=True,
                                    null=True)  # Field name made lowercase.
    cantidad2 = models.DecimalField(db_column='Cantidad2', max_digits=6, decimal_places=2, blank=True,
                                    null=True)  # Field name made lowercase.
    cantidad3 = models.DecimalField(db_column='Cantidad3', max_digits=6, decimal_places=2, blank=True,
                                    null=True)  # Field name made lowercase.
    cantidad4 = models.DecimalField(db_column='Cantidad4', max_digits=6, decimal_places=2, blank=True,
                                    null=True)  # Field name made lowercase.
    precio_credito1 = models.DecimalField(db_column='PrecioCredito1', max_digits=19, decimal_places=4, blank=True,
                                          null=True)  # Field name made lowercase.
    precio_distribuidor1 = models.DecimalField(db_column='PrecioDistribuidor1', max_digits=19, decimal_places=4,
                                               blank=True, null=True)  # Field name made lowercase.
    precio_mayorista1 = models.DecimalField(db_column='PrecioMayorista1', max_digits=19, decimal_places=4, blank=True,
                                            null=True)  # Field name made lowercase.
    precio_credito2 = models.DecimalField(db_column='PrecioCredito2', max_digits=19, decimal_places=4, blank=True,
                                          null=True)  # Field name made lowercase.
    precio_distribuidor2 = models.DecimalField(db_column='PrecioDistribuidor2', max_digits=19, decimal_places=4,
                                               blank=True, null=True)  # Field name made lowercase.
    precio_mayorista2 = models.DecimalField(db_column='PrecioMayorista2', max_digits=19, decimal_places=4, blank=True,
                                            null=True)  # Field name made lowercase.
    precio_credito3 = models.DecimalField(db_column='PrecioCredito3', max_digits=19, decimal_places=4, blank=True,
                                          null=True)  # Field name made lowercase.
    precio_distribuidor3 = models.DecimalField(db_column='PrecioDistribuidor3', max_digits=19, decimal_places=4,
                                               blank=True, null=True)  # Field name made lowercase.
    precio_mayorista3 = models.DecimalField(db_column='PrecioMayorista3', max_digits=19, decimal_places=4, blank=True,
                                            null=True)  # Field name made lowercase.
    precio_credito4 = models.DecimalField(db_column='PrecioCredito4', max_digits=19, decimal_places=4, blank=True,
                                          null=True)  # Field name made lowercase.
    precio_distribuidor4 = models.DecimalField(db_column='PrecioDistribuidor4', max_digits=19, decimal_places=4,
                                               blank=True, null=True)  # Field name made lowercase.
    precio_mayorista4 = models.DecimalField(db_column='PrecioMayorista4', max_digits=19, decimal_places=4, blank=True,
                                            null=True)  # Field name made lowercase.
    nota_compuesto = models.CharField(db_column='NotaCompuesto', max_length=1024, blank=True,
                                      null=True)  # Field name made lowercase.
    nota_promocion = models.CharField(db_column='NotaPromocion', max_length=1024, blank=True,
                                      null=True)  # Field name made lowercase.
    marcaid = models.CharField(db_column='MarcaID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    ubicacionid = models.CharField(db_column='UbicaciónID', max_length=10, blank=True,
                                   null=True)  # Field name made lowercase.
    ptg_descuento1 = models.DecimalField(db_column='PtgDescuento1', max_digits=6, decimal_places=2, blank=True,
                                         null=True)  # Field name made lowercase.

    rentabilidad_costo_contado = models.DecimalField(db_column='RentabilidadCostoContado', max_digits=5,
                                                     decimal_places=2, blank=True, null=True,
                                                     verbose_name='Rent.Contado(%)', default=0)
    rentabilidad_costo_credito = models.DecimalField(db_column='RentabilidadCostoCredito', max_digits=5,
                                                     decimal_places=2, blank=True, null=True,
                                                     verbose_name='Rent.Credito(%)', default=0)
    comision_pvp_contado = models.DecimalField(db_column='ComisionPvpContado', max_digits=5, decimal_places=2,
                                               blank=True, null=True, verbose_name='Comision Contado(%)', default=0)
    comision_pvp_credito = models.DecimalField(db_column='ComisionPvpCredito', max_digits=5, decimal_places=2,
                                               blank=True, null=True, verbose_name='Comision Credito(%)', default=0)

    web_precio_contado = models.DecimalField(db_column='WebPrecioContado', max_digits=19, decimal_places=4, blank=True,
                                             null=True, default=0, verbose_name='Precio de contado')
    web_precio_credito = models.DecimalField(db_column='WebPrecioCredito', max_digits=19, decimal_places=4, blank=True,
                                             null=True, default=0, verbose_name='Precio a credito')

    web_comision_contado = models.DecimalField(db_column='WebComisionContado', max_digits=19, decimal_places=4,
                                               blank=True, null=True, default=0, verbose_name='Comision de contado')
    web_comision_credito = models.DecimalField(db_column='WebComisionCredito', max_digits=19, decimal_places=4,
                                               blank=True, null=True, default=0, verbose_name='Comision a credito')

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        managed = False
        db_table = 'INV_PRODUCTOS'

    def get_bodega_stock(self, bodegaid, sucursalid):
        try:
            return self.invpdbodegastock_set.values(
                'bodega_id', 'bodega__codigo', 'bodega__nombre'
            ).filter(
                bodega_id=bodegaid,
                bodega__sucursal=sucursalid
            ).annotate(
                stock=(Coalesce(Sum('stock'), 0) - Coalesce(Sum('stock_reservado'), 0))
            )[0]
        except:
            pass
        return None

    def get_bodega_stock_sistema(self,bodegaid, sucursalid):
        try:
            return self.invpdbodegastock_set.values(
                'bodega_id', 'bodega__codigo', 'bodega__nombre'
            ).filter(
                bodega_id=bodegaid,
                bodega__sucursal=sucursalid
            ).annotate(
                stock=Coalesce(Sum('stock'), 0)
            )[0]
        except Exception as e:
            pass
        return None

    def get_producto_empaques(self):
        try:
            return self.invproductosempaques_set.filter(
                producto__anulado=False
            ).exclude(codigo_barra='').order_by('factor')
        except:
            pass
        return None

class InvProductosEmpaques(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ID', editable=False)
    producto = models.ForeignKey(InvProductos, models.DO_NOTHING, db_column='ProductoID',
                                 max_length=10)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15, blank=True, null=True)  # Field name made lowercase.
    codigo_barra = models.CharField(db_column='CódigoBarra', max_length=20, blank=True,
                                    null=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    factor = models.DecimalField(db_column='Factor', max_digits=8, decimal_places=3,
                                 default=1)  # Field name made lowercase.
    tasa_utilidad = models.DecimalField(db_column='TasaUtilidad', max_digits=6, decimal_places=2, blank=True,
                                        null=True)  # Field name made lowercase.
    embarque = models.BooleanField(db_column='Embarque', blank=True, null=True)  # Field name made lowercase.
    fijo = models.BooleanField(db_column='Fijo', blank=True, null=True)  # Field name made lowercase.
    precio = models.DecimalField(db_column='Precio', max_digits=19, decimal_places=4, blank=True,
                                 null=True)  # Field name made lowercase.
    grupo = models.CharField(db_column='Grupo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True,
                                  null=True)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,
                            default='')  # Field name made lowercase.
    placa = models.BooleanField(db_column='Placa', blank=True, null=True)  # Field name made lowercase.
    tasa_credito = models.DecimalField(db_column='TasaCredito', max_digits=6, decimal_places=2, blank=True,
                                       null=True)  # Field name made lowercase.
    credito = models.DecimalField(db_column='Credito', max_digits=19, decimal_places=4, blank=True,
                                  null=True)  # Field name made lowercase.
    tasa_distribuidor = models.DecimalField(db_column='TasaDistribuidor', max_digits=6, decimal_places=2, blank=True,
                                            null=True)  # Field name made lowercase.
    distribuidor = models.DecimalField(db_column='Distribuidor', max_digits=19, decimal_places=4, blank=True,
                                       null=True)  # Field name made lowercase.
    tasa_mayorista = models.DecimalField(db_column='TasaMayorista', max_digits=6, decimal_places=2, blank=True,
                                         null=True)  # Field name made lowercase.
    mayorista = models.DecimalField(db_column='Mayorista', max_digits=19, decimal_places=4, blank=True,
                                    null=True)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.producto.nombre)

    class Meta:
        verbose_name = 'Producto empaque'
        verbose_name_plural = 'Producto empaques'
        managed = False
        db_table = 'INV_PRODUCTOS_EMPAQUES'

class InvProductosPrecios(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ID', editable=False)
    producto = models.ForeignKey('InvProductos', models.DO_NOTHING,
                                 db_column='ProductoID')  # Field name made lowercase.
    rango1 = models.DecimalField(db_column='Rango1', max_digits=10, decimal_places=2)  # Field name made lowercase.
    rango2 = models.DecimalField(db_column='Rango2', max_digits=10, decimal_places=2)  # Field name made lowercase.
    precio = models.DecimalField(db_column='Precio', max_digits=19, decimal_places=4, blank=True,
                                 null=True)  # Field name made lowercase.
    precio_final = models.DecimalField(db_column='PrecioFinal', max_digits=19, decimal_places=4, blank=True,
                                       null=True)  # Field name made lowercase.
    precio_credito = models.DecimalField(db_column='PrecioCredito', max_digits=19, decimal_places=4, blank=True,
                                         null=True)  # Field name made lowercase.
    precio_distribuidor = models.DecimalField(db_column='PrecioDistribuidor', max_digits=19, decimal_places=4,
                                              blank=True, null=True)  # Field name made lowercase.
    precio_mayorista = models.DecimalField(db_column='PrecioMayorista', max_digits=19, decimal_places=4, blank=True,
                                           null=True)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True,
                                  null=True)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.producto.nombre)

    class Meta:
        verbose_name = 'Producto empaque'
        verbose_name_plural = 'Producto empaques'
        managed = False
        db_table = 'INV_PRODUCTOS_PRECIOS'

class InvPdBodegaStock(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ID', editable=False)
    producto = models.ForeignKey('InvProductos', models.DO_NOTHING, db_column='ProductoID', max_length=10, blank=True,
                                 null=True)  # Field name made lowercase.
    bodega = models.ForeignKey('InvBodegas', models.DO_NOTHING, db_column='BodegaID', max_length=10, blank=True,
                               null=True)  # Field name made lowercase.
    stock = models.DecimalField(db_column='Stock', max_digits=15, decimal_places=2, blank=True,
                                null=True)  # Field name made lowercase.
    stock_reservado = models.DecimalField(db_column='StockReservado', max_digits=15, decimal_places=2, blank=True,
                                          null=True)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True,
                                  null=True)  # Field name made lowercase.

    ajustado = models.BooleanField(db_column='Ajustado',default=False)
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.producto.nombre)

    class Meta:
        verbose_name = 'Producto bodega stock'
        verbose_name_plural = 'Productos bodega stock'
        managed = False
        db_table = 'INV_PD_BODEGA_STOCK'

    def get_costo_total(self):
        try:
            return round(self.stock * self.producto.costo_promedio,2)
        except:
            pass
        return 0

    def get_cajas(self):
        try:
            return int(self.stock / self.producto.conversion)
        except Exception:
            pass
        return 0

    def get_unidades(self):
        try:
            return round(((self.stock / self.producto.conversion) % 1) * self.producto.conversion,2)
        except Exception:
            pass
        return 0


class InvRubros(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10, editable=False)  # Field name made lowercase.
    codigo = models.CharField(db_column='Código', max_length=15)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10)  # Field name made lowercase.
    ctadebe = models.ForeignKey('contabilidad.AccCuentas', models.DO_NOTHING, db_column='CtaDebeID', max_length=10,
                                related_name='inv_cta_debe_id')  # Field name made lowercase.
    ctahaber = models.ForeignKey('contabilidad.AccCuentas', models.DO_NOTHING, db_column='CtaHaberID', max_length=10,
                                 related_name='inv_cta_haber_id')  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado')  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True,
                                  null=True)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True,
                                  null=True)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        verbose_name = 'Inventario rubro'
        verbose_name_plural = 'Inventario rubros'
        managed = False
        db_table = 'INV_RUBROS'

class InvTransferencias(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10, editable=False)  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10)  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=50, blank=True, null=True,
                               default='')  # Field name made lowercase.
    asientoid = models.CharField(db_column='AsientoID', max_length=10, blank=True, null=True,
                                 default='')  # Field name made lowercase.
    division = models.ForeignKey('sistema.SisDivisiones', db_column='DivisiónID', on_delete=models.DO_NOTHING,
                                 max_length=10, blank=True, null=True, default='')
    fecha = models.DateTimeField(db_column='Fecha')  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True,
                            default='')  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10, blank=True, null=True,
                            default='')  # Field name made lowercase.

    bodega_origen = models.ForeignKey('InvBodegas', models.DO_NOTHING, db_column='BodegaID_Origen', max_length=10,
                                      blank=True, null=True, related_name='pk_bodegaid_origen',
                                      default='')  # Field name made lowercase.
    bodega_destino = models.ForeignKey('InvBodegas', models.DO_NOTHING, db_column='BodegaID_Destino', max_length=10,
                                       blank=True, null=True, related_name='pk_bodegaid_destino',
                                       default='')  # Field name made lowercase.

    bodega_numero_origen = models.CharField(db_column='BodegaNumber_Origen', max_length=10, blank=True, null=True,
                                            default='')  # Field name made lowercase.
    bodega_numero_destino = models.CharField(db_column='BodegaNumber_Destino', max_length=10, blank=True, null=True,
                                             default='')  # Field name made lowercase.

    total = models.DecimalField(db_column='Total', max_digits=19, decimal_places=4,
                                default=0)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True, default='',
                                 editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', auto_now_add=True, blank=True, null=True,
                                      editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True, default='',
                                  editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,
                                       auto_now=True)  # Field name made lowercase.
    procesado = models.BooleanField(db_column='Procesado', default=False)  # Field name made lowercase.
    estado = models.CharField(db_column='estado', choices=ESTADO_TRANSFERENCIA, max_length=1,
                              default='1')  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado', default=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True, default='',
                                  editable=False)  # Field name made lowercase.
    anuladodate = models.DateTimeField(db_column='AnuladoDate', blank=True, null=True,
                                       editable=False)  # Field name made lowercase.
    anuladonota = models.CharField(db_column='AnuladoNota', max_length=1024, blank=True, null=True, default='',
                                   editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True, default='',
                                  editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True, default='',
                            editable=False)  # Field name made lowercase.
    motivoid = models.CharField(db_column='MotivoID', max_length=10, blank=True, null=True,
                                default='')  # Field name made lowercase.

    class Meta:
        verbose_name = 'Transferencia'
        verbose_name_plural = 'Transferencias'
        managed = False
        db_table = 'INV_TRANSFERENCIAS'
        ordering = ['-creadodate']

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
        super(InvTransferencias, self).save(force_insert, force_update, using)

class InvTransferenciasDt(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10, editable=False)  # Field name made lowercase.
    transferencia = models.ForeignKey('InvTransferencias', models.DO_NOTHING, db_column='TransferenciaID',
                                      max_length=10)  # Field name made lowercase.
    producto = models.ForeignKey('InvProductos', models.DO_NOTHING, db_column='ProductoID', max_length=10, blank=True,
                                 null=True)  # Field name made lowercase.
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=11, decimal_places=2, blank=True, null=True,
                                   default=0)  # Field name made lowercase.
    empaque = models.CharField(db_column='Empaque', max_length=40, blank=True, null=True,
                               default='')  # Field name made lowercase.
    costo = models.DecimalField(db_column='Costo', max_digits=19, decimal_places=4,
                                default=0)  # Field name made lowercase.
    factor = models.DecimalField(db_column='Factor', max_digits=6, decimal_places=2,
                                 default=0)  # Field name made lowercase.
    total = models.DecimalField(db_column='Total', max_digits=19, decimal_places=4,
                                default=0)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True, editable=False,
                                  default='')  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,
                            default='')  # Field name made lowercase.

    class Meta:
        verbose_name = 'Transferencia detalle'
        verbose_name_plural = 'InvTransferencias detalles'
        managed = False
        db_table = 'INV_TRANSFERENCIAS_DT'

    def get_producto_stock(self):
        try:
            return round(self.producto.get_bodega_stock(
                self.transferencia.bodega_origen.id,
                self.transferencia.bodega_origen.sucursalid
            )['stock'] / self.producto.conversion, 2)
        except:
            pass
        return 0

    def get_producto_unidades(self):
        return round(self.cantidad * self.factor, 2)

class InvFisico(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10, editable=False)  # Field name made lowercase.
    asientoid = models.CharField(db_column='AsientoID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    bodega = models.ForeignKey('InvBodegas', models.DO_NOTHING, db_column='BodegaID', max_length=10,blank=True, null=True,default='')  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha')  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10,default='')  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=100,blank=True,null=True)  # Field name made lowercase.
    procesado = models.BooleanField(db_column='Procesado',default=False)  # Field name made lowercase.
    estado = models.CharField(db_column='Estado', max_length=1,blank=True,null=True,choices=INV_ESTADO_CONTEO,default='1')  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True,default='')  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,auto_now_add=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,auto_now=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,default='')  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,editable=False)  # Field name made lowercase.
    division = models.ForeignKey('sistema.SisDivisiones', db_column='DivisiónID', on_delete=models.DO_NOTHING,max_length=10, blank=True, null=True, default='')

    class Meta:
        verbose_name = 'Inventario Fisico'
        verbose_name_plural = 'Inventarios Fisico'
        managed = False
        db_table = 'INV_FISICO'
        ordering = ['-creadodate']

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.id = get_contador_sucdiv('INV_TOMA_FISICO-ID-', '{}{}'.format(user.segusuarioparametro.sucursal.codigo,user.segusuarioparametro.division_id[-1]))
                self.numero = self.id
                self.creadopor = user.username
                self.sucursalid = user.segusuarioparametro.sucursal.codigo
                self.estado = '1'
                self.pcid = ''
            else:
                self.editadopor = user.username
        except:
            raise Http404("Error al generar Contador Id..")

        super(InvFisico, self).save(force_insert, force_update, using)


    def get_detalle_productos(self):
        self.invfisicoproductos_set.filter(
            anulado=False
        ).values(
            'producto_id'
        ).annotate(
            unds=Coalesce(Sum(F('cantidad') * F('factor')) , 0)
        ).order_by('producto_id')

class InvFisicoCuentas(models.Model):
    fisico = models.ForeignKey('InvFisico', models.DO_NOTHING, db_column='FísicoID', max_length=10)
    cuentaid = models.ForeignKey('contabilidad.AccCuentas', models.DO_NOTHING, db_column='CuentaID', max_length=10)
    divisaid = models.CharField(db_column='DivisaID', max_length=10,blank=True, null=True)  # Field name made lowercase.
    cambio = models.DecimalField(db_column='Cambio', max_digits=12, decimal_places=6,default=0)  # Field name made lowercase.
    debe = models.DecimalField(db_column='Debe', max_digits=19, decimal_places=4)  # Field name made lowercase.
    haber = models.DecimalField(db_column='Haber', max_digits=19, decimal_places=4)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,auto_now_add=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,editable=False,auto_now=True)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,default='',editable=False)  # Field name made lowercase.

    class Meta:
        verbose_name = 'Inventario Fisico cuentas'
        verbose_name_plural = 'Inventarios Fisico cuentas'
        managed = False
        db_table = 'INV_FISICO_CUENTAS'
        ordering = ['-creadodate']

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
        super(InvFisicoCuentas, self).save(force_insert, force_update, using)

class InvFisicoProductos(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10, editable=False)  # Field name made lowercase.
    fisico = models.ForeignKey('InvFisico', models.DO_NOTHING, db_column='FísicoID', max_length=10)
    producto = models.ForeignKey('InvProductos', models.DO_NOTHING, db_column='ProductoID', max_length=10)
    stock = models.DecimalField(db_column='Stock', max_digits=11, decimal_places=2,default=0)  # Field name made lowercase.
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=11, decimal_places=2,default=0)  # Field name made lowercase.
    diferencia = models.DecimalField(db_column='Diferencia', max_digits=11, decimal_places=2,default=0)  # Field name made lowercase.
    costo = models.DecimalField(db_column='Costo', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    debe = models.DecimalField(db_column='Debe', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    factor = models.DecimalField(db_column='Factor', max_digits=6, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    haber = models.DecimalField(db_column='Haber', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    unidades = models.DecimalField(db_column='Unidades', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    total_unidades = models.DecimalField(db_column='TotalUnidades', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    empaque = models.CharField(db_column='Empaque', max_length=10, blank=True, null=True)  # Field name made lowercase.
    cuentaid = models.CharField(db_column='CuentaID', max_length=10)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,auto_now_add=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,auto_now=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    procesado = models.BooleanField(db_column='Procesado',default=False)  # Field name made lowercase.

    class Meta:
        verbose_name = 'Inventario Fisico productos'
        verbose_name_plural = 'Inventarios Fisico productos'
        managed = False
        db_table = 'INV_FISICO_PRODUCTOS'
        ordering = ['-creadodate']

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
        super(InvFisicoProductos, self).save(force_insert, force_update, using)

    def get_diferencia_productos(self):
        return round(self.stock - self.cantidad,2)

class InvConteo(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    asientoid = models.CharField(db_column='AsientoID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    toma_fisica = models.ForeignKey(InvFisico, models.DO_NOTHING, db_column='TomaFísicaID', max_length=10,blank=True, null=True)
    numero = models.CharField(db_column='Número', max_length=10)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha')  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10,blank=True, null=True)  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=100,blank=True, null=True, default='')  # Field name made lowercase.
    ubicacion = models.CharField(db_column='Ubicación', max_length=50, blank=True, null=True,default='')  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True, default='')  # Field name made lowercase.
    procesado = models.BooleanField(db_column='Procesado',default=False)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    anuladodate = models.DateTimeField(db_column='AnuladoDate', blank=True, null=True)  # Field name made lowercase.
    anuladonota = models.CharField(db_column='AnuladoNota', max_length=1024, blank=True, null=True,default='')  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,auto_now_add=True)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,default='')  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,auto_now=True)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    division = models.ForeignKey('sistema.SisDivisiones', db_column='DivisiónID', on_delete=models.DO_NOTHING,max_length=10, blank=True, null=True, default='')
    conteo1 = models.BooleanField(db_column='Conteo1', default=False)  # Field name made lowercase.
    conteo2 = models.BooleanField(db_column='Conteo2', default=False)  # Field name made lowercase.
    conteo3 = models.BooleanField(db_column='Conteo3', default=False)  # Field name made lowercase.
    ubicacionid = models.CharField(db_column='UbicaciónID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    recontado = models.BooleanField(db_column='Recontado',default=False)  # Field name made lowercase.
    reconteoid = models.CharField(db_column='ReConteoID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    estado = models.CharField(db_column='Estado', max_length=1, blank=True, null=True, choices=INV_ESTADO_CONTEO,default='1')

    class Meta:
        verbose_name = 'Inventario Conteo'
        verbose_name_plural = 'Inventario Conteos'
        managed = False
        db_table = 'INV_CONTEO'
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
        super(InvConteo, self).save(force_insert, force_update, using)

class InvConteoDt(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10, editable=False)
    conteo = models.ForeignKey(InvConteo, models.DO_NOTHING, db_column='ConteoID', max_length=10)
    producto = models.ForeignKey('InvProductos', models.DO_NOTHING, db_column='ProductoID', max_length=10)
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=11, decimal_places=2,default=0)  # Field name made lowercase.
    empaque = models.CharField(db_column='Empaque', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    stock = models.DecimalField(db_column='Stock',max_digits=11, decimal_places=2, blank=True, null=True,default=0)
    factor = models.DecimalField(db_column='Factor',max_digits=6, decimal_places=2, blank=True, null=True,default=0)
    total_unidades = models.DecimalField(db_column='TotalUnidades', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,auto_now_add=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,auto_now=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    recontado = models.BooleanField(db_column='Recontado',default=False)  # Field name made lowercase.
    totalconteo1 = models.DecimalField(db_column='TotalConteo1', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    totalconteo2 = models.DecimalField(db_column='TotalConteo2', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    diferencia = models.DecimalField(db_column='Diferencia', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    egreso = models.BooleanField(db_column='Egreso',default=False)  # Field name made lowercase.
    ingreso = models.BooleanField(db_column='Ingreso',default=False)  # Field name made lowercase.
    ajuste = models.BooleanField(db_column='Ajuste',default=False)  # Field name made lowercase.
    procesado = models.BooleanField(db_column='Procesado',default=False)  # Field name made lowercase.
    transferencia = models.BooleanField(db_column='Transferencia',default=False)  # Field name made lowercase.

    class Meta:
        verbose_name = 'Inventario Conteo Detalle'
        verbose_name_plural = 'Inventario Conteos Detalles'
        managed = False
        db_table = 'INV_CONTEO_DT'
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
        super(InvConteoDt, self).save(force_insert, force_update, using)

class InvIngresos(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    asientoid = models.CharField(db_column='AsientoID', max_length=10,blank=True, null=True,default='')  # Field name made lowercase.
    ordenid = models.CharField(db_column='OrdenID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    bodega = models.ForeignKey('InvBodegas', models.DO_NOTHING, db_column='BodegaID', max_length=10, blank=True,null=True, default='')  # Field name made lowercase.
    bodega_num = models.CharField(db_column='Bodega_Num', max_length=10, blank=True, null=True)  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha')  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=100)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10)  # Field name made lowercase.
    valor_base = models.DecimalField(db_column='Valor_Base', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True,default='')  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    anuladodate = models.DateTimeField(db_column='AnuladoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladonota = models.CharField(db_column='AnuladoNota', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,auto_now_add=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    division = models.ForeignKey('sistema.SisDivisiones', db_column='DivisiónID', on_delete=models.DO_NOTHING,max_length=10, blank=True, null=True, default='')
    motivoid = models.CharField(db_column='MotivoID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    numcartilla = models.CharField(db_column='NumCartilla', max_length=15, blank=True, null=True,default='')  # Field name made lowercase.
    sucursalcode = models.CharField(db_column='SucursalCode', max_length=2, blank=True, null=True,default='')  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,editable=False,auto_now=True)  # Field name made lowercase.

    class Meta:
        verbose_name = 'Inventario Ingreso'
        verbose_name_plural = 'Inventario Ingresos'
        managed = False
        db_table = 'INV_INGRESOS'
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
        super(InvIngresos, self).save(force_insert, force_update, using)

class InvIngresosProductos(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    ingreso = models.ForeignKey(InvIngresos, models.DO_NOTHING, db_column='IngresoID', max_length=10)
    ordendtid = models.CharField(db_column='OrdenDTID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    producto = models.ForeignKey('InvProductos', models.DO_NOTHING, db_column='ProductoID', max_length=10)
    bodega = models.ForeignKey('InvBodegas', models.DO_NOTHING, db_column='BodegaID', max_length=10, blank=True,null=True, default='')  # Field name made lowercase.
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=11, decimal_places=2,default=0)  # Field name made lowercase.
    docenade = models.DecimalField(db_column='Docenade', max_digits=6, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    decenade = models.DecimalField(db_column='DecenaDe', max_digits=6, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    empaque = models.CharField(db_column='Empaque', max_length=40, blank=True, null=True,default='')  # Field name made lowercase.
    factor = models.DecimalField(db_column='Factor', max_digits=6, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    costo = models.DecimalField(db_column='Costo', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    divisaid = models.CharField(db_column='DivisaID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    cambio = models.DecimalField(db_column='Cambio', max_digits=12, decimal_places=6,default=0)  # Field name made lowercase.
    cta_mayor = models.ForeignKey('contabilidad.AccCuentas', models.DO_NOTHING, db_column='CtaMayorID', max_length=10,blank=True, null=True,default='')
    promocion = models.BooleanField(db_column='Promoción',default=False)  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,auto_now_add=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    unidades = models.DecimalField(db_column='Unidades', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    tipo_tabla = models.CharField(db_column='TipoTabla', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        verbose_name = 'Inventario Ingreso Producto'
        verbose_name_plural = 'Inventario Ingresos Productos'
        managed = False
        db_table = 'INV_INGRESOS_PRODUCTOS'
        ordering = ['-creadodate']

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.creadopor = user.username
        except:
            pass
        super(InvIngresosProductos, self).save(force_insert, force_update, using)

class InvEgresos(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    asientoid = models.CharField(db_column='AsientoID', max_length=10)  # Field name made lowercase.
    bodega = models.ForeignKey('InvBodegas', models.DO_NOTHING, db_column='BodegaID', max_length=10, blank=True,null=True, default='')  # Field name made lowercase.
    bodega_num = models.CharField(db_column='Bodega_Num', max_length=10, blank=True, null=True)  # Field name made lowercase.
    numero = models.CharField(db_column='Número', max_length=10)  # Field name made lowercase.
    ordenid = models.CharField(db_column='OrdenID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha')  # Field name made lowercase.
    detalle = models.CharField(db_column='Detalle', max_length=100,default='')  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10)  # Field name made lowercase.
    valor_base = models.DecimalField(db_column='Valor_Base', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    despachado = models.BooleanField(db_column='Despachado',default=False)  # Field name made lowercase.
    nota = models.CharField(db_column='Nota', max_length=1024, blank=True, null=True,default='')  # Field name made lowercase.
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    anuladopor = models.CharField(db_column='AnuladoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    anuladodate = models.DateTimeField(db_column='AnuladoDate', blank=True, null=True,editable=False)  # Field name made lowercase.
    anuladonota = models.CharField(db_column='AnuladoNota', max_length=1024, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,default='',editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,auto_now_add=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,editable=False,auto_now=True)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    division = models.ForeignKey('sistema.SisDivisiones', db_column='DivisiónID', on_delete=models.DO_NOTHING,max_length=10, blank=True, null=True, default='')
    motivoid = models.CharField(db_column='MotivoID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    responsableid = models.CharField(db_column='ResponsableID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    numcartilla = models.CharField(db_column='NumCartilla', max_length=15, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        verbose_name = 'Inventario Egreso'
        verbose_name_plural = 'Inventario Egresos'
        managed = False
        db_table = 'INV_EGRESOS'
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
        super(InvEgresos, self).save(force_insert, force_update, using)

class InvEgresosProductos(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10,editable=False)  # Field name made lowercase.
    egreso = models.ForeignKey(InvEgresos, models.DO_NOTHING, db_column='EgresoID', max_length=10)
    ordendtid = models.CharField(db_column='OrdenDTID', max_length=10, blank=True, null=True,default='')  # Field name made lowercase.
    producto = models.ForeignKey('InvProductos', models.DO_NOTHING, db_column='ProductoID', max_length=10)
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=11, decimal_places=2,default=0)  # Field name made lowercase.
    entregado = models.DecimalField(db_column='Entregado', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    stock = models.DecimalField(db_column='Stock', max_digits=11, decimal_places=2,default=0)  # Field name made lowercase.
    empaque = models.CharField(db_column='Empaque', max_length=40, blank=True, null=True,default='')  # Field name made lowercase.
    factor = models.DecimalField(db_column='Factor', max_digits=6, decimal_places=2,default=0)  # Field name made lowercase.
    costo = models.DecimalField(db_column='Costo', max_digits=19, decimal_places=4,default=0)  # Field name made lowercase.
    cta_mayor = models.ForeignKey('contabilidad.AccCuentas', models.DO_NOTHING, db_column='CtaMayorID', max_length=10,blank=True, null=True, default='')
    anulado = models.BooleanField(db_column='Anulado',default=False)  # Field name made lowercase.
    creadopor = models.CharField(db_column='CreadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    creadodate = models.DateTimeField(db_column='CreadoDate', blank=True, null=True,auto_now_add=True,editable=False)  # Field name made lowercase.
    editadopor = models.CharField(db_column='EditadoPor', max_length=15, blank=True, null=True,editable=False)  # Field name made lowercase.
    editadodate = models.DateTimeField(db_column='EditadoDate', blank=True, null=True,auto_now=True,editable=False)  # Field name made lowercase.
    sucursalid = models.CharField(db_column='SucursalID', max_length=2, blank=True, null=True,editable=False)  # Field name made lowercase.
    pcid = models.CharField(db_column='PcID', max_length=50, blank=True, null=True,editable=False,default='')  # Field name made lowercase.
    unidades = models.DecimalField(db_column='Unidades', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.
    precio = models.DecimalField(db_column='Precio', max_digits=19, decimal_places=4, blank=True, null=True,default=0)  # Field name made lowercase.
    devuelto = models.DecimalField(db_column='Devuelto', max_digits=11, decimal_places=2, blank=True, null=True,default=0)  # Field name made lowercase.

    class Meta:
        verbose_name = 'Inventario Egreso Producto'
        verbose_name_plural = 'Inventario Egresos Productos'
        managed = False
        db_table = 'INV_EGRESOS_PRODUCTOS'
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
        super(InvEgresosProductos, self).save(force_insert, force_update, using)
