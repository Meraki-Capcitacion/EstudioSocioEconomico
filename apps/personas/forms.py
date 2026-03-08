from django import forms

from .models import Persona, SaludPersona


class DateInput(forms.DateInput):
    """Widget de fecha que renderiza <input type="date">."""
    input_type = 'date'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('format', '%Y-%m-%d')
        super().__init__(*args, **kwargs)


class PersonaForm(forms.ModelForm):
    """
    Formulario para crear y editar Persona.

    El campo fecha_nacimiento usa type="date" para que el navegador
    muestre su selector nativo de calendario.
    """

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
            'activo',
        ]
        widgets = {
            'fecha_nacimiento': DateInput(),
        }


class SaludPersonaForm(forms.ModelForm):
    """Formulario para crear y editar SaludPersona. Sin campos de fecha."""

    class Meta:
        model = SaludPersona
        fields = [
            'persona', 'nivel_salud',
            'enfermedades_cronicas', 'antecedentes_familiares',
            'consumo_sustancias',
        ]
