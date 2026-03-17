from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import PerfilUsuario, PermisoModulo


class PermisoModuloInline(admin.TabularInline):
    model = PermisoModulo
    extra = 0
    verbose_name = 'Módulo permitido'
    verbose_name_plural = 'Módulos permitidos'


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil y rol'
    fields = ('rol', 'telefono', 'activo')
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = [PerfilUsuarioInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol', 'telefono', 'activo', 'usa_permisos_personalizados', 'created_at')
    list_filter = ('rol', 'activo')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name')
    list_editable = ('rol', 'activo')
    inlines = [PermisoModuloInline]

    @admin.display(boolean=True, description='Permisos personalizados')
    def usa_permisos_personalizados(self, obj):
        return obj.usa_permisos_personalizados


@admin.register(PermisoModulo)
class PermisoModuloAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'modulo')
    list_filter = ('modulo', 'perfil__rol')
    search_fields = ('perfil__usuario__username', 'perfil__usuario__first_name')
