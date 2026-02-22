from django.contrib import admin

from .models import Persona, SaludPersona
from apps.domicilios.models import Domicilio
from apps.educacion.models import Educacion, Idioma
from apps.laboral.models import HistorialLaboral
from apps.familia.models import GrupoFamiliar
from apps.referencias.models import Referencia
from apps.documentos.models import Documento


class DomicilioInline(admin.StackedInline):
    model = Domicilio
    extra = 0
    fieldsets = (
        ('Tipo y dirección', {
            'fields': ('tipo', 'calle', 'numero_exterior', 'numero_interior',
                       'entre_calles', 'colonia', 'codigo_postal',
                       'municipio', 'estado', 'pais'),
        }),
        ('Vivienda', {
            'fields': ('tipo_inmueble', 'tipo_vivienda', 'propietario_nombre',
                       'material_construccion', 'numero_habitaciones',
                       'numero_niveles', 'superficie_m2'),
        }),
        ('Espacios del inmueble', {
            'fields': ('tiene_sala', 'tiene_cocina', 'tiene_comedor',
                       'tiene_patio_servicio', 'tiene_cochera'),
            'classes': ('collapse',),
        }),
        ('Materiales de construcción', {
            'fields': ('tiene_piso', 'tiene_piso_cemento', 'tiene_enjarre',
                       'tiene_paredes_sin_enjarre', 'tiene_techo_lamina',
                       'tiene_loza', 'tiene_puertas'),
            'classes': ('collapse',),
        }),
        ('Servicios', {
            'fields': ('tiene_agua', 'tiene_luz', 'tiene_drenaje', 'tiene_gas',
                       'tiene_internet', 'tiene_tv_cable',
                       'tiene_pavimentacion', 'tiene_telefono_domicilio'),
            'classes': ('collapse',),
        }),
        ('Valuación y condición', {
            'fields': ('valor_inmueble', 'valor_muebles',
                       'valor_electrodomesticos', 'orden_limpieza'),
            'classes': ('collapse',),
        }),
        ('Tiempo de residencia', {
            'fields': ('tiempo_residencia_anios', 'tiempo_residencia_meses'),
        }),
    )


class EducacionInline(admin.TabularInline):
    model = Educacion
    extra = 0
    fields = ('nivel', 'institucion', 'ciudad_institucion', 'titulo',
              'estado', 'anio_inicio', 'anio_fin',
              'tipo_documento_estudio', 'documento_verificado')


class IdiomaInline(admin.TabularInline):
    model = Idioma
    extra = 0
    fields = ('idioma', 'porcentaje_habla', 'porcentaje_escribe',
              'porcentaje_lee', 'plantel', 'tiene_certificacion',
              'tipo_certificacion', 'nivel_certificacion')


class HistorialLaboralInline(admin.TabularInline):
    model = HistorialLaboral
    extra = 0
    fields = ('empresa', 'puesto', 'fecha_inicio', 'fecha_fin',
              'es_trabajo_actual', 'salario_final', 'verificada')


class GrupoFamiliarInline(admin.TabularInline):
    model = GrupoFamiliar
    extra = 0
    fields = ('nombre_completo', 'parentesco', 'edad', 'telefono',
              'tipo_dependencia', 'vive_en_domicilio', 'ciudad_residencia',
              'aporta_ingreso', 'monto_aportacion')


class ReferenciaInline(admin.TabularInline):
    model = Referencia
    extra = 0
    fields = ('tipo', 'nombre', 'telefono',
              'parentesco_o_relacion', 'tiempo_conocer_anios', 'verificada')


class DocumentoPersonaInline(admin.TabularInline):
    model = Documento
    extra = 0
    fields = ('tipo', 'archivo', 'nombre_archivo', 'verificado')
    readonly_fields = ('nombre_archivo',)


class SaludPersonaInline(admin.StackedInline):
    model = SaludPersona
    extra = 0
    max_num = 1
    fieldsets = (
        ('Estado de salud', {
            'fields': ('nivel_salud', 'enfermedades_cronicas',
                       'antecedentes_familiares', 'consumo_sustancias'),
        }),
    )


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('folio', 'get_nombre_completo', 'curp',
                    'telefono_movil', 'estado_civil', 'activo')
    list_filter = ('activo', 'estado_civil', 'tipo_identificacion')
    search_fields = ('folio', 'nombre', 'apellido_paterno',
                     'apellido_materno', 'curp', 'email', 'nss')
    readonly_fields = ('folio', 'created_at', 'updated_at',
                       'created_by', 'updated_by')
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Información básica', {
            'fields': ('folio', 'nombre', 'apellido_paterno',
                       'apellido_materno', 'fecha_nacimiento',
                       'lugar_nacimiento'),
        }),
        ('Identificación oficial', {
            'fields': ('tipo_identificacion', 'numero_identificacion',
                       'curp', 'rfc', 'nss',
                       'licencia_manejo_folio', 'cartilla_militar_folio',
                       'acta_nacimiento_numero'),
        }),
        ('Contacto', {
            'fields': ('email', 'telefono_movil', 'telefono_fijo',
                       'facebook_perfil'),
        }),
        ('Estado civil y familia', {
            'fields': ('estado_civil', 'numero_dependientes'),
        }),
        ('Datos físicos', {
            'fields': ('peso', 'estatura'),
        }),
        ('Historial personal', {
            'fields': ('historial_residencias', 'periodos_sin_laborar',
                       'actividades_tiempo_libre'),
            'classes': ('collapse',),
        }),
        ('Control', {
            'fields': ('activo',),
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at',
                       'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    inlines = [SaludPersonaInline, DomicilioInline, EducacionInline,
               IdiomaInline, HistorialLaboralInline, GrupoFamiliarInline,
               ReferenciaInline, DocumentoPersonaInline]

    @admin.display(description='Nombre completo')
    def get_nombre_completo(self, obj):
        return obj.nombre_completo

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SaludPersona)
class SaludPersonaAdmin(admin.ModelAdmin):
    list_display = ('persona', 'nivel_salud')
    list_filter = ('nivel_salud',)
    search_fields = ('persona__folio', 'persona__nombre',
                     'persona__apellido_paterno')
    raw_id_fields = ('persona',)
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    list_per_page = 25

    fieldsets = (
        ('Persona', {
            'fields': ('persona',),
        }),
        ('Estado de salud', {
            'fields': ('nivel_salud', 'enfermedades_cronicas',
                       'antecedentes_familiares', 'consumo_sustancias'),
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
