from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.configuracion.models import TimestampModel
from apps.personas.models import Persona


class GrupoFamiliar(TimestampModel):
    """Modelo de miembros del grupo familiar"""
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='grupo_familiar')

    nombre_completo = models.CharField(max_length=300)
    parentesco = models.CharField(max_length=100)
    edad = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)])

    TIPO_DEPENDENCIA = [
        ('TOT', 'Total'),
        ('PAR', 'Parcial'),
        ('IND', 'Independiente'),
        ('ECO', 'Aporta económicamente'),
    ]
    tipo_dependencia = models.CharField(max_length=3, choices=TIPO_DEPENDENCIA)

    ocupacion = models.CharField(max_length=200, blank=True)
    escolaridad = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=15, blank=True, verbose_name='Teléfono del familiar')

    vive_en_domicilio = models.BooleanField(default=True)
    ciudad_residencia = models.CharField(
        max_length=100, blank=True,
        verbose_name='Ciudad de residencia',
        help_text='Completar si el familiar no vive en el domicilio del solicitante'
    )
    aporta_ingreso = models.BooleanField(default=False)
    monto_aportacion = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name_plural = "Grupos familiares"

    def __str__(self):
        return f"{self.nombre_completo} - {self.parentesco}"
