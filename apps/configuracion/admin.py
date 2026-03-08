from django import forms
from django.contrib import admin

from .models import EmpresaCliente, TipoEstudio
from .widgets import SeccionesWidget


# ---------------------------------------------------------------------------
# Formulario personalizado para TipoEstudio
# ---------------------------------------------------------------------------
class TipoEstudioAdminForm(forms.ModelForm):
    """
    Reemplaza el widget por defecto del JSONField `secciones` con
    SeccionesWidget (drag-and-drop con SortableJS).
    """

    class Meta:
        model = TipoEstudio
        fields = '__all__'
        widgets = {
            'secciones': SeccionesWidget(),
        }

    def clean_secciones(self):
        """
        Garantiza que las secciones obligatorias siempre estén presentes.
        Las agrega al inicio si el usuario las removió (no debería ocurrir
        porque el JS lo impide, pero es una segunda línea de defensa).
        """
        valor = self.cleaned_data.get('secciones') or []
        obligatorias = TipoEstudio.SECCIONES_OBLIGATORIAS
        for codigo in sorted(obligatorias):
            if codigo not in valor:
                valor.insert(0, codigo)
        return valor


# ---------------------------------------------------------------------------
# EmpresaClienteAdmin  (sin cambios)
# ---------------------------------------------------------------------------
@admin.register(EmpresaCliente)
class EmpresaClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'created_at')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    list_editable = ('activo',)


# ---------------------------------------------------------------------------
# TipoEstudioAdmin
# ---------------------------------------------------------------------------
@admin.register(TipoEstudio)
class TipoEstudioAdmin(admin.ModelAdmin):
    form = TipoEstudioAdminForm

    list_display = (
        'nombre',
        'activo',
        'requiere_visita',
        'requiere_verificacion_laboral',
        'puntuacion_minima_aprobacion',
        'orden',
    )
    list_filter = ('activo', 'requiere_visita', 'requiere_verificacion_laboral')
    list_editable = ('activo', 'orden')
    search_fields = ('nombre', 'descripcion')
    ordering = ('orden', 'nombre')

    fieldsets = (
        (
            'Información general',
            {
                'fields': ('nombre', 'descripcion', 'activo', 'orden'),
            },
        ),
        (
            'Requisitos del estudio',
            {
                'fields': (
                    'requiere_visita',
                    'requiere_verificacion_laboral',
                    'puntuacion_minima_aprobacion',
                ),
            },
        ),
        (
            'Secciones incluidas',
            {
                'fields': ('secciones',),
                'description': (
                    'Arrastra las secciones para definir cuáles se incluyen '
                    'en este tipo de estudio y en qué orden aparecen. '
                    'Las secciones con candado (<b>candidato</b> y '
                    '<b>evaluacion</b>) son obligatorias.'
                ),
                'classes': ('wide',),
            },
        ),
    )
