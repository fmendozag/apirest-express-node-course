# -*- coding: utf-8 -*-
from decimal import Decimal
USER_PERMISO_ELIMINAR = (
    1,  # Administradores
)
USER_ALL_PERMISOS = (
    1,  # Administradores,
    9,
    2
)
SEXO = (
    (1, 'HOMBRE'),
    (2, 'MUJER'),
    (3, 'S/N'),
)
GENERO = (
    (1, 'MASCULINO'),
    (2, 'FEMENINO'),
    (3, 'S/N'),
)
TIPO_DOCUMENTO = (
    (1, 'CEDULA'),
    (2, 'PASAPORTE'),
)

ESTADO_CIVIL = (
    (1, 'SOLTERO(A)'),
    (2, 'CASADO(A)'),
    (3, 'DIVORCIADO(A)'),
    (4, 'UNIÓN LIBRE'),
    (5, 'VIUDO(A)'),
    (6, 'SIN ESPECIFICAR/')
)

TIPO_DOCUMENTO_FACTURA = (
    ('VEN-FA    ','VEN-FA'),
    ('POS-NV    ','POS-NV'),
    ('POS-FA    ','POS-FA'),
)
ESTADO_COMISION = (
        ('1', 'C.TOTAL'),
        ('2', 'C.PARCIAL'),
        ('3', 'PENDIENTE'),
        ('4', 'SUPERVISION')
    )

TIPO_DOCUMENTO_COMISION = (
        ('VEN-FA','VEN-FA'),
        ('COM-IN','COM-IN'),
    )

DIAS_SEMANA=(
    ('1','LUNES'),
    ('2','MARTES'),
    ('3','MIERCOLES'),
    ('4','JUEVES'),
    ('5','VIERNES'),
    ('6','SABADO'),
    ('7','DOMINGO'),
)
USUARIOS_NEMESIS = (
    'T & T - 01',
    'T & T - 02',
    'T & T - 03',
)

LISTA_PRECIOS = (
    (1,'CONTADO'),
    (2,'COBERTURA'),
    (3,'DISTRIBUIDOR'),
    (4,'MAYORISTA'),
    (5,'COSTO'),
)

ESTADO_ORDEN_PEDIDO = (
    ('1','PENDIENTE'),
    ('2','APROBADO'),
    ('3','ANULADO'),
    ('4','OBSERVADO'),
    ('5','PROCESADA'),
)

ESTADO_TRANSFERENCIA = (
    ('1','PENDIENTE'),
    ('2','PROCESADA'),
    ('3','ANULADO')
)

TIPO_MODELO = (
    ('1','ALMACEN'),
    ('2','COBERTURA'),
    ('3','MAYORISTA'),
)

INV_ESTADO_CONTEO = (
    ('1','PENDIENTE'),
    ('2','PROCESADA'),
    ('3','ANULADO')
)
TIPO_TRANSFERENCIA= (
    ('INV-TR','TRANSFERENCIA'),
    ('INV-TRF','INV FISICO'),
('INV-TRS','SUG.TRANSFERENCIA'),)

NOMBRE_INSTITUCION = 'SUPERMERCADOS BELBRY'
INSTITUCION_DIRECCION = ''
INSTITUCION_DIRECCION2 = ''
INSTITUCION_TELEFONO = '04-9999999'
INSTITUCION_CIUDAD = 'Milagro'
LOGO_INFORME_CABECERA = 'logo-informe-cabecera.png'

DNS = 'belbry.com.ec'
LOGO_SISTEMA = 'fa fa-cart-plus fa-1x'
NOMBRE_SISTEMA = 'WEB | BelBry '
SISTEMA_AUTOR = 'Ing. Ernesto Guamán U.'
CIUDAD_DEFAULT = 1
USER_PASSWORD_DEFAULT = '123456'
DIVISA_ID = '0000000001'

#URL_WEB = 'http://istvr.edu.ec/'
#URL_SAYA = 'http://www.sayavr.istvr.edu.ec:8080/'

PORCENTAJE_COMISION = Decimal('11.11')
# DEBUG	10
# INFO	20
# SUCCESS	25
# WARNING	30
# ERROR	40

MINIMO_ABONO = Decimal('0.20')
MAXIMO_DIAS_CREDITO = 30
VALOR_COMISION = Decimal('20.00')
UBICACION_ID = '0000000011'
PEDIDOS_CONTROLA_STOCK = 1

