from django.contrib import admin

from .models import NivelEducativo, Educacion, Idioma


@admin.register(NivelEducativo)
class NivelEducativoAdmin(admin.ModelAdmin):
    list_display = ('nivel', 'orden', 'activo')
    list_editable = ('activo', 'orden')
    list_filter = ('activo',)
    search_fields = ('nivel',)


@admin.register(Educacion)
class EducacionAdmin(admin.ModelAdmin):
    list_display = ('persona', 'nivel', 'institucion', 'ciudad_institucion',
                    'titulo', 'estado', 'anio_inicio', 'anio_fin',
                    'tipo_documento_estudio', 'documento_verificado')
    list_filter = ('nivel', 'estado', 'tipo_documento_estudio',
                   'documento_verificado')
    search_fields = ('persona__folio', 'persona__nombre',
                     'institucion', 'titulo', 'ciudad_institucion')
    raw_id_fields = ('persona',)
    readonly_fields = ('created_at', 'updated_at',
                       'created_by', 'updated_by')
    list_per_page = 25

    fieldsets = (
        ('Persona', {
            'fields': ('persona',),
        }),
        ('Formación', {
            'fields': ('nivel', 'institucion', 'ciudad_institucion',
                       'titulo', 'estado', 'anio_inicio', 'anio_fin'),
        }),
        ('Documentos y verificación', {
            'fields': ('tipo_documento_estudio', 'tiene_cedula',
                       'numero_cedula', 'documento_verificado'),
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at',
                       'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Idioma)
class IdiomaAdmin(admin.ModelAdmin):
    list_display = ('persona', 'idioma', 'porcentaje_habla',
                    'porcentaje_escribe', 'porcentaje_lee',
                    'tiene_certificacion', 'tipo_certificacion')
    list_filter = ('tiene_certificacion', 'idioma')
    search_fields = ('persona__folio', 'persona__nombre',
                     'idioma', 'tipo_certificacion', 'plantel')
    raw_id_fields = ('persona',)
    readonly_fields = ('created_at', 'updated_at',
                       'created_by', 'updated_by')
    list_per_page = 25

    fieldsets = (
        ('Persona', {
            'fields': ('persona',),
        }),
        ('Idioma y dominio', {
            'fields': ('idioma', 'porcentaje_habla', 'porcentaje_escribe',
                       'porcentaje_lee'),
        }),
        ('Estudio del idioma', {
            'fields': ('plantel', 'periodo_inicio', 'periodo_fin'),
        }),
        ('Certificación', {
            'fields': ('tiene_certificacion', 'tipo_certificacion',
                       'nivel_certificacion'),
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at',
                       'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
