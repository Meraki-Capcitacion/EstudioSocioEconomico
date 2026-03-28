import uuid

from django.db import models
from django.utils import timezone

from apps.configuracion.models import EmpresaCliente, TimestampModel, TipoEstudio
from apps.personas.models import Persona

class EstudioSocioeconomico(TimestampModel):
    """Modelo principal del estudio socioeconómico"""
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='estudios')
    tipo_estudio = models.ForeignKey(TipoEstudio, on_delete=models.PROTECT)
    empresa_cliente = models.ForeignKey(
        EmpresaCliente, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='estudios',
        verbose_name='Empresa que solicita el estudio'
    )

    ESTADO_ESTUDIO = [
        ('BOR', 'Borrador'),
        ('VIS', 'Visita programada'),
        ('PRO', 'En proceso'),
        ('COM', 'Completado'),
        ('REV', 'En revisión'),
        ('APR', 'Confiable'),
        ('REC', 'No confiable'),
        ('CAN', 'Cancelado'),
    ]
    estado = models.CharField(max_length=3, choices=ESTADO_ESTUDIO, default='BOR')

    fecha_programada_visita = models.DateTimeField(null=True, blank=True)
    fecha_realizacion = models.DateTimeField(null=True, blank=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)

    observaciones = models.TextField(blank=True)
    conclusion = models.TextField(blank=True)
    puntuacion_total = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Contexto de la solicitud / reclutamiento
    expectativas_salariales = models.CharField(
        max_length=200, blank=True,
        verbose_name='Expectativas económicas para la vacante'
    )
    MEDIO_ENTERADO = [
        ('FAC', 'Facebook'),
        ('WSK', 'WhatsApp'),
        ('REF', 'Referencia'),
        ('OTR', 'Otro'),
    ]
    medio_enterado_vacante = models.CharField(
        max_length=3, choices=MEDIO_ENTERADO, blank=True,
        verbose_name='Medio por el que se enteró de la vacante'
    )
    tiempo_traslado = models.CharField(
        max_length=100, blank=True,
        verbose_name='Tiempo aproximado de traslado domicilio-empresa'
    )
    comentarios_adicionales = models.TextField(
        blank=True,
        verbose_name='Comentarios adicionales del solicitante'
    )

    # Conclusión del evaluador (para el reporte PDF)
    aspectos_positivos = models.TextField(
        blank=True,
        verbose_name='Aspectos positivos'
    )
    aspectos_negativos = models.TextField(
        blank=True,
        verbose_name='Aspectos negativos / áreas de oportunidad'
    )

    class Meta:
        verbose_name_plural = "Estudios socioeconómicos"
        ordering = ['-created_at']

    def __str__(self):
        return f"Estudio {self.persona.folio} - {self.get_estado_display()}"


class EstudioToken(models.Model):
    """Token UUID de acceso público para que el candidato complete su estudio de forma autogestionada"""
    estudio = models.OneToOneField(
        EstudioSocioeconomico, on_delete=models.CASCADE, related_name='token'
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    activo = models.BooleanField(default=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Token de estudio"
        verbose_name_plural = "Tokens de estudio"

    def __str__(self):
        return f"Token {self.token} — {self.estudio}"

    @property
    def vigente(self):
        if not self.activo:
            return False
        if self.fecha_expiracion and timezone.now() > self.fecha_expiracion:
            return False
        return True

    @property
    def completado(self):
        """
        True cuando el candidato finalizó el portal (activo=False por acción del candidato).
        Se diferencia de expirado porque la fecha_expiracion no ha pasado o no existe.
        """
        if self.activo:
            return False
        # Si la fecha de expiración aún no ha pasado (o no tiene), fue completado por el candidato
        if self.fecha_expiracion is None:
            return True
        return timezone.now() <= self.fecha_expiracion

    @property
    def expirado(self):
        """True cuando el token venció sin que el candidato lo completara."""
        if not self.activo:
            return False
        return bool(self.fecha_expiracion and timezone.now() > self.fecha_expiracion)
