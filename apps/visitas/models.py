from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.configuracion.models import TimestampModel
from apps.estudios.models import EstudioSocioeconomico


class VisitaDomiciliaria(TimestampModel):
    """Modelo para la visita domiciliaria"""
    estudio = models.ForeignKey(EstudioSocioeconomico, on_delete=models.CASCADE, related_name='visitas')
    evaluador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='visitas_realizadas')

    fecha_visita = models.DateTimeField()
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Resultados de la visita
    persona_encontrada = models.BooleanField(default=True)
    verificacion_domicilio = models.BooleanField(default=False)

    # Entorno
    TIPO_ZONA = [
        ('RES', 'Residencial'),
        ('MIX', 'Mixto'),
        ('POP', 'Popular'),
        ('RUR', 'Rural'),
        ('IND', 'Industrial'),
    ]
    tipo_zona = models.CharField(max_length=3, choices=TIPO_ZONA)
    nivel_seguridad = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    nivel_ruido = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    acceso_transporte = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    # Comentarios
    observaciones_generales = models.TextField(blank=True)
    comentarios_colonos = models.TextField(
        blank=True,
        verbose_name='Comentarios de vecinos / colonos'
    )
    recomendacion = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Visitas domiciliarias"

    def __str__(self):
        return f"Visita {self.estudio.persona.folio} - {self.fecha_visita.strftime('%d/%m/%Y')}"
