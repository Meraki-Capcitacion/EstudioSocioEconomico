from django import forms

from .models import HistorialLaboral


class DateInput(forms.DateInput):
    """Widget de fecha que renderiza <input type="date">."""
    input_type = 'date'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('format', '%Y-%m-%d')
        super().__init__(*args, **kwargs)


class DateTimeLocalInput(forms.DateTimeInput):
    """Widget de fecha-hora que renderiza <input type="datetime-local">."""
    input_type = 'datetime-local'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('format', '%Y-%m-%dT%H:%M')
        super().__init__(*args, **kwargs)


class HistorialLaboralForm(forms.ModelForm):
    """
    Formulario para crear y editar HistorialLaboral.

    - fecha_inicio y fecha_fin usan type="date" (DateField).
    - fecha_verificacion usa type="datetime-local" (DateTimeField).
    """

    class Meta:
        model = HistorialLaboral
        fields = [
            'persona', 'empresa', 'puesto', 'telefono_empresa',
            'fecha_inicio', 'fecha_fin', 'es_trabajo_actual',
            'salario_inicial', 'salario_final',
            'nombre_jefe', 'telefono_jefe', 'motivo_separacion',
            'verificada', 'fecha_verificacion',
        ]
        widgets = {
            'fecha_inicio': DateInput(),
            'fecha_fin': DateInput(),
            'fecha_verificacion': DateTimeLocalInput(attrs={'class': 'fecha-input'}),
        }
