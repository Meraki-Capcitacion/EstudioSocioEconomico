from django import forms
from .models import GrupoFamiliar


class GrupoFamiliarForm(forms.ModelForm):

    class Meta:
        model = GrupoFamiliar
        fields = [
            'persona', 'nombre_completo', 'parentesco', 'edad',
            'tipo_dependencia', 'ocupacion', 'escolaridad',
            'vive_en_domicilio', 'aporta_ingreso', 'monto_aportacion',
            'telefono', 'ciudad_residencia',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['monto_aportacion'].required = False

    def clean(self):
        cleaned_data = super().clean()
        aporta = cleaned_data.get('aporta_ingreso', False)
        if not aporta:
            cleaned_data['monto_aportacion'] = 0
        elif cleaned_data.get('monto_aportacion') is None:
            self.add_error('monto_aportacion', 'Ingresa el monto de aportación.')
        return cleaned_data
