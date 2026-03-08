from django import forms

from .models import Referencia


class DateTimeLocalInput(forms.DateTimeInput):
    """Widget de fecha-hora que renderiza <input type="datetime-local">."""
    input_type = 'datetime-local'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('format', '%Y-%m-%dT%H:%M')
        super().__init__(*args, **kwargs)


class ReferenciaForm(forms.ModelForm):
    """
    Formulario para crear y editar Referencia.

    fecha_verificacion usa type="datetime-local" (DateTimeField).
    El campo se incluye aquí aunque no aparezca en el template principal,
    por consistencia y para que esté disponible si se agrega.
    """

    class Meta:
        model = Referencia
        fields = [
            'persona', 'tipo', 'nombre', 'telefono', 'email',
            'parentesco_o_relacion', 'tiempo_conocer_anios', 'domicilio',
            'actividad_tiempo_libre', 'lugares_laborado', 'conducta', 'cualidades',
            'verificada', 'comentarios_verificacion',
        ]
        widgets = {
            'fecha_verificacion': DateTimeLocalInput(attrs={'class': 'fecha-input'}),
        }
