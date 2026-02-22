from django.contrib import admin

from .models import EmpresaCliente, TipoEstudio


@admin.register(EmpresaCliente)
class EmpresaClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'created_at')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    list_editable = ('activo',)


@admin.register(TipoEstudio)
class TipoEstudioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'requiere_visita',
                    'requiere_verificacion_laboral',
                    'puntuacion_minima_aprobacion', 'orden')
    list_filter = ('activo', 'requiere_visita', 'requiere_verificacion_laboral')
    list_editable = ('activo', 'orden')
    search_fields = ('nombre', 'descripcion')
    ordering = ('orden', 'nombre')
