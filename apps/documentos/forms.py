from django import forms
from django.urls import reverse_lazy

from .models import Documento
from apps.estudios.models import EstudioSocioeconomico


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = [
            'persona', 'estudio', 'tipo',
            'archivo', 'nombre_archivo',
            'verificado', 'verificado_por',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Determinar qué persona está seleccionada
        persona_id = None
        if self.instance.pk and self.instance.persona_id:
            persona_id = self.instance.persona_id
        elif self.initial.get('persona'):
            persona_id = self.initial['persona']
        elif self.data.get('persona'):
            persona_id = self.data['persona']

        # Filtrar estudios por persona seleccionada
        if persona_id:
            self.fields['estudio'].queryset = EstudioSocioeconomico.objects.filter(
                persona_id=persona_id
            )
        else:
            self.fields['estudio'].queryset = EstudioSocioeconomico.objects.none()

        # nombre_archivo es opcional en el form (se auto-llena desde el archivo)
        self.fields['nombre_archivo'].required = False

        # HTMX: al cambiar persona, recargar opciones de estudio
        self.fields['persona'].widget.attrs.update({
            'hx-get': '/documentos/estudios-por-persona/',
            'hx-target': '#id_estudio',
            'hx-trigger': 'change',
            'hx-swap': 'innerHTML',
        })
