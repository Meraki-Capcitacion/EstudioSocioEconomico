from django.contrib import admin

from .models import Domicilio


@admin.register(Domicilio)
class DomicilioAdmin(admin.ModelAdmin):
    list_display = ('persona', 'tipo', 'tipo_inmueble', 'calle', 'colonia',
                    'municipio', 'estado', 'tipo_vivienda', 'orden_limpieza')
    list_filter = ('tipo', 'tipo_inmueble', 'tipo_vivienda', 'estado',
                   'orden_limpieza')
    search_fields = ('persona__folio', 'persona__nombre',
                     'calle', 'colonia', 'codigo_postal')
    raw_id_fields = ('persona',)
    readonly_fields = ('created_at', 'updated_at',
                       'created_by', 'updated_by')
    list_per_page = 25

    fieldsets = (
        ('Persona', {
            'fields': ('persona', 'tipo'),
        }),
        ('Dirección', {
            'fields': ('calle', 'numero_exterior', 'numero_interior',
                       'entre_calles', 'colonia', 'codigo_postal',
                       'municipio', 'estado', 'pais'),
        }),
        ('Características de la vivienda', {
            'fields': ('tipo_inmueble', 'tipo_vivienda', 'propietario_nombre',
                       'material_construccion', 'numero_habitaciones',
                       'numero_niveles', 'superficie_m2'),
        }),
        ('Espacios del inmueble', {
            'fields': ('tiene_sala', 'tiene_cocina', 'tiene_comedor',
                       'tiene_patio_servicio', 'tiene_cochera'),
        }),
        ('Materiales de construcción', {
            'fields': ('tiene_piso', 'tiene_piso_cemento', 'tiene_enjarre',
                       'tiene_paredes_sin_enjarre', 'tiene_techo_lamina',
                       'tiene_loza', 'tiene_puertas'),
        }),
        ('Servicios', {
            'fields': ('tiene_agua', 'tiene_luz', 'tiene_drenaje', 'tiene_gas',
                       'tiene_internet', 'tiene_tv_cable',
                       'tiene_pavimentacion', 'tiene_telefono_domicilio'),
        }),
        ('Valuación y condición general', {
            'fields': ('valor_inmueble', 'valor_muebles',
                       'valor_electrodomesticos', 'orden_limpieza'),
        }),
        ('Tiempo de residencia', {
            'fields': ('tiempo_residencia_anios', 'tiempo_residencia_meses'),
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
