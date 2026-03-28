from django import forms
from django.contrib.auth.models import User

from .models import PerfilUsuario


class CrearUsuarioForm(forms.Form):
    """Formulario para crear un nuevo usuario del sistema (solo superusuarios)."""
    first_name = forms.CharField(
        label='Nombre(s)', max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm text-sm',
            'placeholder': 'Ej: Juan Carlos',
            'autofocus': True,
        }),
    )
    last_name = forms.CharField(
        label='Apellidos', max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm text-sm',
            'placeholder': 'Ej: García López',
        }),
    )
    username = forms.CharField(
        label='Nombre de usuario', max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm text-sm font-mono',
            'placeholder': 'Ej: jgarcia',
        }),
    )
    email = forms.EmailField(
        label='Correo electrónico', required=False,
        widget=forms.EmailInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm text-sm',
            'placeholder': 'usuario@empresa.com',
        }),
    )
    rol = forms.ChoiceField(
        label='Rol en el sistema',
        choices=PerfilUsuario.ROL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm text-sm',
        }),
    )
    password1 = forms.CharField(
        label='Contraseña', min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm text-sm',
            'placeholder': 'Mínimo 8 caracteres',
        }),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm text-sm',
            'placeholder': 'Repite la contraseña',
        }),
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip().lower()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Ya existe un usuario con ese nombre de usuario.')
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            password=data['password1'],
            first_name=data['first_name'].strip().title(),
            last_name=data['last_name'].strip().title(),
            email=data.get('email', ''),
        )
        perfil, _ = PerfilUsuario.objects.get_or_create(usuario=user, defaults={'rol': data['rol']})
        perfil.rol = data['rol']
        perfil.save()
        return user


class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['rol', 'telefono']
        widgets = {
            'rol': forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm text-sm'}),
            'telefono': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm text-sm',
                'placeholder': '10 dígitos',
            }),
        }
        labels = {
            'rol': 'Rol en el sistema',
            'telefono': 'Teléfono de contacto',
        }
