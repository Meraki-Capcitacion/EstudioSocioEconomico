from django import forms

from .models import EstudioSocioeconomico


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


class EstudioSocioeconomicoForm(forms.ModelForm):
    """
    Formulario para crear y editar EstudioSocioeconomico.

    Los campos DateTimeField usan type="datetime-local" para que el
    navegador muestre su selector nativo de fecha y hora.
    """

    class Meta:
        model = EstudioSocioeconomico
        fields = [
            'persona', 'empresa_cliente', 'tipo_estudio', 'estado',
            'fecha_programada_visita', 'fecha_realizacion', 'fecha_aprobacion',
            'observaciones', 'conclusion', 'aspectos_positivos', 'aspectos_negativos',
            'expectativas_salariales', 'medio_enterado_vacante',
            'tiempo_traslado', 'comentarios_adicionales',
        ]
        widgets = {
            'fecha_programada_visita': DateTimeLocalInput(attrs={'class': 'fecha-input'}),
            'fecha_realizacion': DateTimeLocalInput(attrs={'class': 'fecha-input'}),
            'fecha_aprobacion': DateTimeLocalInput(attrs={'class': 'fecha-input'}),
        }
