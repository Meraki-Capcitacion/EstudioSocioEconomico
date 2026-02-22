from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.configuracion.models import TimestampModel
from apps.personas.models import Persona


class NivelEducativo(models.Model):
    """Catálogo de niveles educativos"""
    nivel = models.CharField(max_length=100)
    orden = models.IntegerField(unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Niveles educativos"
        ordering = ['orden']

    def __str__(self):
        return self.nivel


class Educacion(TimestampModel):
    """Modelo de formación educativa"""
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='educacion')
    nivel = models.ForeignKey(NivelEducativo, on_delete=models.PROTECT)

    institucion = models.CharField(max_length=200)
    ciudad_institucion = models.CharField(
        max_length=100, blank=True,
        verbose_name='Ciudad donde se localiza la institución'
    )
    titulo = models.CharField(max_length=200)

    ESTADO_EDUCATIVO = [
        ('INC', 'Incompleto'),
        ('COM', 'Completo'),
        ('TRU', 'Trunco'),
        ('CUR', 'Cursando'),
    ]
    estado = models.CharField(max_length=3, choices=ESTADO_EDUCATIVO)

    anio_inicio = models.IntegerField()
    anio_fin = models.IntegerField(null=True, blank=True)

    TIPO_DOCUMENTO_ESTUDIO = [
        ('CER', 'Certificado'),
        ('TIT', 'Título'),
        ('CON', 'Constancia'),
        ('CAR', 'Carta de pasante'),
        ('OTR', 'Otro'),
        ('NIN', 'Ninguno'),
    ]
    tipo_documento_estudio = models.CharField(
        max_length=3, choices=TIPO_DOCUMENTO_ESTUDIO, blank=True,
        verbose_name='Tipo de documento de estudio obtenido'
    )

    tiene_cedula = models.BooleanField(default=False)
    numero_cedula = models.CharField(max_length=20, blank=True)

    documento_verificado = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Educación"
        ordering = ['-anio_fin', '-anio_inicio']

    def __str__(self):
        return f"{self.nivel} - {self.institucion}"


class Idioma(TimestampModel):
    """Dominio de idiomas adicionales al español"""
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='idiomas')

    idioma = models.CharField(max_length=100, verbose_name='Idioma')
    porcentaje_habla = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='% de dominio oral (habla)'
    )
    porcentaje_escribe = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='% de dominio escrito'
    )
    porcentaje_lee = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='% de comprensión lectora'
    )
    plantel = models.CharField(
        max_length=200, blank=True,
        verbose_name='Plantel / institución donde lo estudió'
    )
    periodo_inicio = models.IntegerField(
        null=True, blank=True,
        verbose_name='Año de inicio del estudio'
    )
    periodo_fin = models.IntegerField(
        null=True, blank=True,
        verbose_name='Año de fin del estudio'
    )
    tiene_certificacion = models.BooleanField(
        default=False,
        verbose_name='Cuenta con certificación oficial'
    )
    tipo_certificacion = models.CharField(
        max_length=100, blank=True,
        verbose_name='Tipo de certificación (TOEFL, IELTS, DELF, etc.)'
    )
    nivel_certificacion = models.CharField(
        max_length=100, blank=True,
        verbose_name='Nivel que acredita la certificación'
    )

    class Meta:
        verbose_name = "Idioma"
        verbose_name_plural = "Idiomas"
        ordering = ['idioma']

    def __str__(self):
        return f"{self.idioma} – {self.persona.nombre_completo}"
