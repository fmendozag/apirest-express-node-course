from django.contrib import admin
# Register your models here.
from acreedor.models import AcrAcreedores,AcrGrupos

class AcrAcreedoresProxy(AcrAcreedores):
    class Meta:
        proxy = True
        verbose_name = 'Acreedor Visita'
        verbose_name_plural = 'Acreedores Visitas'
        managed = False

class AcrAcreedoresAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Datos del Proveedor', {
            'fields': [
                ('codigo','nombre',)
            ]
        }),
        ('Orden Compra', {
            'fields': [
                ('frecuenciavisita', 'plazoentregaminimo','plazoentregamaximo',),
            ]
        }),
    ]

    list_display = (
        'codigo',
        'nombre',
        'frecuenciavisita',
        'plazoentregaminimo',
        'plazoentregamaximo',
    )
    list_per_page = 10
    ordering = ('-creadodate',)
    search_fields = ('codigo','nombre',)
    list_filter = (
        'codigo',
    )

admin.site.register(AcrAcreedoresProxy,AcrAcreedoresAdmin)

admin.site.register(AcrGrupos)
admin.site.register(AcrAcreedores)
