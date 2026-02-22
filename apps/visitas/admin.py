from django.contrib import admin

from .models import VisitaDomiciliaria


@admin.register(VisitaDomiciliaria)
class VisitaDomiciliariaAdmin(admin.ModelAdmin):
    list_display = ('estudio', 'evaluador', 'fecha_visita',
                    'persona_encontrada', 'verificacion_domicilio',
                    'tipo_zona')
    list_filter = ('tipo_zona', 'persona_encontrada',
                   'verificacion_domicilio')
    search_fields = ('estudio__persona__folio',
                     'estudio__persona__nombre',
                     'evaluador__username')
    raw_id_fields = ('estudio',)
    readonly_fields = ('created_at', 'updated_at',
                       'created_by', 'updated_by')
    date_hierarchy = 'fecha_visita'
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('estudio', 'evaluador', 'fecha_visita'),
        }),
        ('Ubicación GPS', {
            'fields': ('latitud', 'longitud'),
            'classes': ('collapse',),
        }),
        ('Resultados de la visita', {
            'fields': ('persona_encontrada', 'verificacion_domicilio'),
        }),
        ('Entorno', {
            'fields': ('tipo_zona', 'nivel_seguridad',
                       'nivel_ruido', 'acceso_transporte'),
        }),
        ('Comentarios', {
            'fields': ('observaciones_generales', 'comentarios_colonos',
                       'recomendacion'),
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
