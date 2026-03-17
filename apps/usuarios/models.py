from django.contrib.auth.models import User
from django.db import models


MODULOS_DISPONIBLES = [
    ('personas', 'Personas'),
    ('estudios', 'Estudios Socioeconómicos'),
    ('domicilios', 'Domicilios'),
    ('educacion', 'Educación e Idiomas'),
    ('laboral', 'Historial Laboral'),
    ('familia', 'Grupo Familiar'),
    ('referencias', 'Referencias'),
    ('economia', 'Situación Económica'),
    ('visitas', 'Visitas Domiciliarias'),
    ('evaluacion', 'Evaluación de Riesgo'),
    ('documentos', 'Documentos'),
    ('notificaciones', 'Notificaciones'),
    ('reportes', 'Reportes PDF'),
    ('configuracion', 'Configuración'),
]

_TODOS_LOS_MODULOS = {m[0] for m in MODULOS_DISPONIBLES}

# Módulos por defecto según el rol (cuando no hay configuración explícita)
MODULOS_POR_ROL_DEFAULT = {
    'ANA': _TODOS_LOS_MODULOS,
    'INS': {'visitas', 'referencias', 'laboral', 'documentos', 'notificaciones'},
    'AUD': _TODOS_LOS_MODULOS,
}


class PerfilUsuario(models.Model):
    """
    Extiende auth.User con el rol operativo dentro del sistema.

    Roles:
      ANA — Analista: acceso completo por defecto.
      INS — Inspector: acceso a visitas, laboral, referencias, documentos y notificaciones.
      AUD — Auditor: acceso de revisión (todos los módulos por defecto, configurable).

    Los módulos accesibles se configuran individualmente mediante PermisoModulo.
    Si no hay permisos explícitos, se aplican los defaults del rol.
    """
    ROL_CHOICES = [
        ('ANA', 'Analista'),
        ('INS', 'Inspector'),
        ('AUD', 'Auditor'),
    ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario',
    )
    rol = models.CharField(
        max_length=3,
        choices=ROL_CHOICES,
        default='ANA',
        verbose_name='Rol',
        help_text='Determina las funciones a las que tiene acceso el usuario.',
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Teléfono',
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Desactiva para suspender el acceso sin borrar el usuario.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'
        ordering = ['usuario__last_name', 'usuario__first_name']

    def __str__(self):
        nombre = self.usuario.get_full_name() or self.usuario.username
        return f'{nombre} ({self.get_rol_display()})'

    @property
    def es_analista(self):
        return self.rol == 'ANA'

    @property
    def es_inspector(self):
        return self.rol == 'INS'

    @property
    def es_auditor(self):
        return self.rol == 'AUD'

    @property
    def usa_permisos_personalizados(self):
        """True si el perfil tiene permisos configurados explícitamente."""
        return self.permisos_modulos.exists()

    def tiene_permiso_modulo(self, modulo):
        """
        Devuelve True si el perfil tiene acceso al módulo indicado.
        Usa permisos explícitos si existen; si no, aplica los defaults del rol.
        """
        if self.permisos_modulos.exists():
            return self.permisos_modulos.filter(modulo=modulo).exists()
        return modulo in MODULOS_POR_ROL_DEFAULT.get(self.rol, set())

    def get_modulos_permitidos(self):
        """Devuelve el conjunto de claves de módulos permitidos para este perfil."""
        if self.permisos_modulos.exists():
            return set(self.permisos_modulos.values_list('modulo', flat=True))
        return set(MODULOS_POR_ROL_DEFAULT.get(self.rol, set()))


class PermisoModulo(models.Model):
    """
    Asignación explícita de un módulo a un perfil de usuario.
    Si un perfil tiene al menos un registro aquí, se usan los permisos explícitos.
    Si no tiene ninguno, se aplican los defaults del rol.
    """
    perfil = models.ForeignKey(
        PerfilUsuario,
        on_delete=models.CASCADE,
        related_name='permisos_modulos',
        verbose_name='Perfil',
    )
    modulo = models.CharField(
        max_length=20,
        choices=MODULOS_DISPONIBLES,
        verbose_name='Módulo',
    )

    class Meta:
        verbose_name = 'Permiso de módulo'
        verbose_name_plural = 'Permisos de módulos'
        unique_together = [('perfil', 'modulo')]
        ordering = ['modulo']

    def __str__(self):
        return f'{self.perfil} — {self.get_modulo_display()}'
