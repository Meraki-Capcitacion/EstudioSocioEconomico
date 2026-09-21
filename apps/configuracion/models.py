from django.contrib.auth.models import User
from django.db import models

class TimestampModel(models.Model):
    """Modelo abstracto con campos de tiempo comunes"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="%(class)s_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="%(class)s_updated")

    class Meta:
        abstract = True

class EmpresaCliente(models.Model):
    """Empresa o cliente que solicita el estudio socioeconómico"""
    nombre = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='empresas/logos/', null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Empresa cliente"
        verbose_name_plural = "Empresas clientes"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class TipoEstudio(models.Model):
    """Catálogo de tipos de estudio socioeconómico"""

    SECCIONES_DISPONIBLES = [
        ('candidato',   'Portal del Candidato'),
        ('domicilios',  'Domicilio'),
        ('educacion',   'Educación e Idiomas'),
        ('salud',       'Salud'),
        ('laboral',     'Historial Laboral'),
        ('familia',     'Grupo Familiar'),
        ('referencias', 'Referencias'),
        ('economia',    'Situación Económica'),
        ('visitas',     'Visita Domiciliaria'),
        ('evaluacion',  'Evaluación de Riesgo'),
        ('documentos',  'Documentos'),
    ]
    SECCIONES_OBLIGATORIAS = frozenset({'candidato', 'evaluacion'})

    # Pestaña sintética: siempre se muestra y no es configurable por tipo.
    SECCION_RESUMEN = ('resumen', 'Resumen')


    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    # Campos de control
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Configuración específica por tipo de estudio
    requiere_visita = models.BooleanField(default=True)
    requiere_verificacion_laboral = models.BooleanField(default=True)
    puntuacion_minima_aprobacion = models.IntegerField(default=70)

    secciones = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Secciones del estudio',
        help_text=(
            'Secciones incluidas en este tipo de estudio '
            '(candidato y evaluacion son obligatorias)'
        ),
    )

    class Meta:
        verbose_name = "Tipo de estudio"
        verbose_name_plural = "Tipos de estudio"
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

    @classmethod
    def etiquetas_secciones(cls):
        """Mapa clave -> etiqueta de las secciones válidas."""
        return dict(cls.SECCIONES_DISPONIBLES)

    @classmethod
    def tabs_por_defecto(cls):
        """Pestañas usadas cuando el estudio no tiene tipo asignado."""
        return [cls.SECCION_RESUMEN] + list(cls.SECCIONES_DISPONIBLES)

    def tabs(self):
        """
        Pestañas del expediente como lista de tuplas (clave, etiqueta).

        Las claves salen siempre de SECCIONES_DISPONIBLES, que es el
        vocabulario canónico: la plantilla nombra sus paneles con esas
        mismas claves (id="tab-<clave>"). Cualquier valor guardado en
        `secciones` que no exista en el catálogo se descarta, para que un
        dato viejo o mal escrito no produzca una pestaña sin panel.
        """
        etiquetas = self.etiquetas_secciones()
        claves = [
            s for s in (self.secciones or [])
            if isinstance(s, str) and s in etiquetas
        ]
        if not claves:
            return self.tabs_por_defecto()
        return [self.SECCION_RESUMEN] + [(c, etiquetas[c]) for c in claves]