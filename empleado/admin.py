from django.contrib import admin

# Register your models here.
from empleado.models import *

class EmpEmpleadosAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'cedula',
        'nombre',
        'grupo',
        'zona',
        'estado',
    )
    list_per_page = 20
    ordering = ('-creadodate',)
    search_fields = ('codigo','cedula', 'nombre')
    list_filter = (
        'grupo',
        'sucursalid',
        'anulado',
    )
    def estado(self, obj):
        return not obj.anulado
    estado.boolean = True

admin.site.register(EmpGrupos)
admin.site.register(EmpEmpleados,EmpEmpleadosAdmin)
