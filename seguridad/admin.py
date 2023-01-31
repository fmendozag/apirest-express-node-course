from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from seguridad.models import SegModulo, SegModuloGrupo, SegUsuarioParametro, SegUsuarioFoto

class SegModuloAdmin(admin.ModelAdmin):
    list_display = (
        'url',
        'nombre',
        'tipo',
        'clase',
        'item_orden',
        'activo',
    )
    list_per_page = 20
    ordering = ('tipo','nombre')
    search_fields = ('codigo','nombre')
    list_filter = (
        'tipo',
        'activo'
    )
admin.site.register(SegModulo,SegModuloAdmin)

class SegModuloGrupoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'descripcion',
        'prioridad',
        'activo',
    )
    list_per_page = 20
    ordering = ('prioridad','nombre',)
    search_fields = ('nombre',)
    list_filter = (
        'activo',
    )
admin.site.register(SegModuloGrupo,SegModuloGrupoAdmin)

class UsuarioParametroInline(admin.StackedInline):
    model = SegUsuarioParametro
    can_delete = False

class UsuarioFotoInline(admin.StackedInline):
    model = SegUsuarioFoto
    can_delete = False

class UsuarioParametroAdmin(UserAdmin):
    inlines = [UsuarioFotoInline,UsuarioParametroInline]

admin.site.unregister(User)
admin.site.register(User, UsuarioParametroAdmin)
