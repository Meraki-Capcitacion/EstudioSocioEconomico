"""Formularios para el portal público de autogestión del candidato (Escenario A)."""
from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from apps.personas.models import Persona, SaludPersona
from apps.domicilios.models import Domicilio
from apps.educacion.models import Educacion, Idioma
from apps.familia.models import GrupoFamiliar
from apps.economia.models import SituacionEconomica
from apps.referencias.models import Referencia
from apps.laboral.models import HistorialLaboral
from apps.documentos.models import Documento


class Paso1PersonaForm(forms.ModelForm):
    """Paso 1 — Datos personales e identificaciones."""
    class Meta:
        model = Persona
        fields = [
            'nombre', 'apellido_paterno', 'apellido_materno',
            'fecha_nacimiento', 'lugar_nacimiento',
            'tipo_identificacion', 'numero_identificacion',
            'curp', 'rfc', 'nss',
            'licencia_manejo_folio', 'cartilla_militar_folio', 'acta_nacimiento_numero',
            'email', 'telefono_movil', 'telefono_fijo', 'facebook_perfil',
            'estado_civil', 'numero_dependientes',
            'peso', 'estatura',
            'historial_residencias', 'periodos_sin_laborar', 'actividades_tiempo_libre',
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'historial_residencias': forms.Textarea(attrs={'rows': 3}),
            'periodos_sin_laborar': forms.Textarea(attrs={'rows': 3}),
            'actividades_tiempo_libre': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500')


class Paso2DomicilioForm(forms.ModelForm):
    """Paso 2 — Domicilio y características del inmueble."""
    class Meta:
        model = Domicilio
        exclude = ['persona', 'tipo', 'created_at', 'updated_at', 'created_by', 'updated_by']
        widgets = {
            'observaciones_inmueble': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        if args and args[0]:
            data = args[0].copy()
            if 'valor_inmueble' in data:
                data['valor_inmueble'] = data['valor_inmueble'].replace(',', '')
            args = (data,) + args[1:]
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'h-4 w-4 text-purple-600 rounded border-gray-300 focus:ring-purple-500')
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500')
            else:
                field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500')


class Paso3EducacionForm(forms.ModelForm):
    """Paso 3a — Registro de nivel educativo."""
    class Meta:
        model = Educacion
        exclude = ['persona', 'documento_verificado', 'created_at', 'updated_at', 'created_by', 'updated_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500')
            else:
                field.widget.attrs.setdefault('class', 'h-4 w-4 text-purple-600 rounded border-gray-300 focus:ring-purple-500')


class Paso3IdiomaForm(forms.ModelForm):
    """Paso 3b — Registro de idioma."""
    class Meta:
        model = Idioma
        exclude = ['persona', 'created_at', 'updated_at', 'created_by', 'updated_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500')


class Paso3SaludForm(forms.ModelForm):
    """Paso 3c — Información de salud."""
    class Meta:
        model = SaludPersona
        exclude = ['persona', 'created_at', 'updated_at', 'created_by', 'updated_by']
        widgets = {
            'enfermedades_cronicas': forms.Textarea(attrs={'rows': 3}),
            'antecedentes_familiares': forms.Textarea(attrs={'rows': 3}),
            'consumo_sustancias': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500')
            else:
                field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500')


class Paso4FamiliarForm(forms.ModelForm):
    """Paso 4 — Miembro del grupo familiar."""
    class Meta:
        model = GrupoFamiliar
        exclude = [
            'persona', 'created_at', 'updated_at', 'created_by', 'updated_by',
            'escolaridad', 'telefono', 'ciudad_residencia',
            'aporta_ingreso', 'monto_aportacion',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'h-4 w-4 text-purple-600 rounded border-gray-300 focus:ring-purple-500')
            else:
                field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500')


class Paso5EconomiaForm(forms.ModelForm):
    """Paso 5 — Situación económica y patrimonio."""

    _CAMPOS_DECIMALES = [
        'salario_mensual', 'bonos_comisiones', 'ingresos_extra', 'apoyo_familiar', 'otros_ingresos',
        'gasto_alimentacion', 'gasto_vivienda', 'gasto_servicios', 'gasto_transporte',
        'gasto_educacion', 'gasto_salud', 'gasto_deudas', 'otros_gastos',
        'automovil_valor_comercial', 'credito_hipotecario', 'credito_automotriz',
        'tarjetas_credito', 'tienda_departamental_adeudo', 'prestamos_personales', 'otros_creditos',
    ]

    class Meta:
        model = SituacionEconomica
        exclude = ['estudio']
        widgets = {
            'descripcion_patrimonio': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # Limpiar comas de los campos decimales antes de que Django valide
        if args and args[0]:
            data = args[0].copy()
            for nombre in self._CAMPOS_DECIMALES:
                if nombre in data:
                    data[nombre] = data[nombre].replace(',', '')
            # otros_creditos no se renderiza en el portal; inyectar default 0
            if 'otros_creditos' not in data:
                data['otros_creditos'] = '0'
            args = (data,) + args[1:]
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'h-4 w-4 text-purple-600 rounded border-gray-300 focus:ring-purple-500')
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500')
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500')
            else:
                field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500')


class Paso6ReferenciaForm(forms.ModelForm):
    """Paso 6 — Referencia personal."""
    class Meta:
        model = Referencia
        fields = [
            'tipo', 'nombre', 'telefono', 'email',
            'parentesco_o_relacion', 'tiempo_conocer_anios', 'domicilio',
        ]
        widgets = {
            'domicilio': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500')
            else:
                field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500')


class Paso7LaboralForm(forms.ModelForm):
    """Paso 7a — Historial laboral."""
    fecha_inicio = forms.IntegerField(
        min_value=1950, max_value=2100, label='Año de inicio',
        widget=forms.NumberInput(attrs={'placeholder': 'Ej: 2020', 'min': 1950, 'max': 2100}),
    )
    fecha_fin = forms.IntegerField(
        min_value=1950, max_value=2100, required=False, label='Año de salida',
        widget=forms.NumberInput(attrs={'placeholder': 'Ej: 2023', 'min': 1950, 'max': 2100}),
    )

    class Meta:
        model = HistorialLaboral
        exclude = ['persona', 'verificada', 'fecha_verificacion', 'created_at', 'updated_at', 'created_by', 'updated_by']
        widgets = {
            'motivo_separacion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        if args and args[0]:
            data = args[0].copy()
            for campo in ('salario_inicial', 'salario_final'):
                if campo in data:
                    data[campo] = data[campo].replace(',', '')
            args = (data,) + args[1:]
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'h-4 w-4 text-purple-600 rounded border-gray-300 focus:ring-purple-500')
            else:
                field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500')

    def clean(self):
        from datetime import date
        cleaned = super().clean()
        anio_inicio = cleaned.get('fecha_inicio')
        anio_fin = cleaned.get('fecha_fin')
        if anio_inicio:
            cleaned['fecha_inicio'] = date(anio_inicio, 1, 1)
        if anio_fin:
            cleaned['fecha_fin'] = date(anio_fin, 1, 1)
        es_actual = cleaned.get('es_trabajo_actual', False)
        if not es_actual and not anio_fin:
            self.add_error('fecha_fin', 'Indica el año de salida, o marca que es tu trabajo actual.')
        return cleaned


class Paso7DocumentoForm(forms.ModelForm):
    """Paso 7b — Subida de documentos y fotografías."""
    class Meta:
        model = Documento
        fields = ['tipo', 'archivo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archivo'].widget.attrs.update({
            'accept': 'image/*,application/pdf',
            'capture': 'environment',
            'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100',
        })
        self.fields['tipo'].widget.attrs.update({
            'class': 'w-full rounded-lg border-gray-300 focus:ring-purple-500 focus:border-purple-500',
        })
        # Solo mostrar tipos relevantes para el candidato
        self.fields['tipo'].choices = [
            ('IDE', 'Identificación oficial'),
            ('DOM', 'Comprobante de domicilio'),
            ('ING', 'Comprobante de ingresos'),
            ('TIT', 'Título/Cédula profesional'),
            ('ACT', 'Acta de nacimiento'),
            ('CUR', 'CURP'),
            ('FOT', 'Fotografía'),
            ('OTR', 'Otro documento'),
        ]

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            if archivo.size > 10 * 1024 * 1024:  # 10 MB
                raise ValidationError('El archivo no puede superar los 10 MB.')
        return archivo
