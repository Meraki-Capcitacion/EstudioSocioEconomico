from django.contrib import admin

from .models import GrupoFamiliar


@admin.register(GrupoFamiliar)
class GrupoFamiliarAdmin(admin.ModelAdmin):
    list_display = ('persona', 'nombre_completo', 'parentesco',
                    'edad', 'telefono', 'tipo_dependencia',
                    'vive_en_domicilio', 'aporta_ingreso',
                    'monto_aportacion')
    list_filter = ('tipo_dependencia', 'vive_en_domicilio', 'aporta_ingreso')
    search_fields = ('persona__folio', 'persona__nombre',
                     'nombre_completo', 'parentesco', 'telefono')
    raw_id_fields = ('persona',)
    readonly_fields = ('created_at', 'updated_at',
                       'created_by', 'updated_by')
    list_per_page = 25

    fieldsets = (
        ('Persona evaluada', {
            'fields': ('persona',),
        }),
        ('Datos del familiar', {
            'fields': ('nombre_completo', 'parentesco', 'edad',
                       'ocupacion', 'escolaridad', 'telefono'),
        }),
        ('Residencia y dependencia', {
            'fields': ('tipo_dependencia', 'vive_en_domicilio',
                       'ciudad_residencia', 'aporta_ingreso',
                       'monto_aportacion'),
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
