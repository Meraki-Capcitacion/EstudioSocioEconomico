from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone

from apps.configuracion.models import TimestampModel


class Persona(TimestampModel):
    """Modelo principal de la persona evaluada"""
    # Información básica
    folio = models.CharField(max_length=20, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    lugar_nacimiento = models.CharField(max_length=200, blank=True, verbose_name='Lugar de nacimiento')

    # Identificación oficial
    TIPO_IDENTIFICACION = [
        ('INE', 'INE/IFE'),
        ('PAS', 'Pasaporte'),
        ('CED', 'Cédula Profesional'),
        ('CAR', 'Cartilla Militar'),
        ('OTR', 'Otro'),
    ]
    tipo_identificacion = models.CharField(max_length=3, choices=TIPO_IDENTIFICACION, blank=True)
    numero_identificacion = models.CharField(max_length=50, blank=True)
    curp = models.CharField(max_length=18, blank=True, validators=[RegexValidator(r'^$|^[A-Z0-9]{18}$', 'CURP inválida (debe tener 18 caracteres alfanuméricos en mayúsculas)')])
    rfc = models.CharField(max_length=13, blank=True, validators=[RegexValidator(r'^[A-Z&Ñ]{4}\d{6}[A-Z0-9]{3}$', 'RFC inválido')])
    nss = models.CharField(max_length=11, blank=True, verbose_name='NSS (Número de Seguridad Social)')
    licencia_manejo_folio = models.CharField(max_length=50, blank=True, verbose_name='Folio de licencia de manejo')
    cartilla_militar_folio = models.CharField(max_length=50, blank=True, verbose_name='Folio de cartilla militar')
    acta_nacimiento_numero = models.CharField(max_length=50, blank=True, verbose_name='Número de acta de nacimiento')

    # Contacto
    email = models.EmailField()
    telefono_movil = models.CharField(max_length=15)
    telefono_fijo = models.CharField(max_length=15, blank=True)
    facebook_perfil = models.CharField(max_length=200, blank=True, verbose_name='Perfil de Facebook')

    # Estado civil y familia
    ESTADO_CIVIL = [
        ('SOL', 'Soltero/a'),
        ('CAS', 'Casado/a'),
        ('ULB', 'Unión Libre'),
        ('DIV', 'Divorciado/a'),
        ('VIU', 'Viudo/a'),
        ('SEP', 'Separado/a'),
        ('OTR', 'Otro'),
    ]
    estado_civil = models.CharField(max_length=3, choices=ESTADO_CIVIL, blank=True)
    numero_dependientes = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    # Datos físicos
    peso = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name='Peso (kg)',
        validators=[MinValueValidator(0), MaxValueValidator(999)]
    )
    estatura = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name='Estatura (cm)',
        validators=[MinValueValidator(0), MaxValueValidator(999)]
    )

    # Historial y contexto personal
    historial_residencias = models.TextField(
        blank=True,
        verbose_name='Historial de residencias anteriores',
        help_text='Lugar, período (año inicio-fin) y motivo del cambio de residencia'
    )
    periodos_sin_laborar = models.TextField(
        blank=True,
        verbose_name='Períodos sin laborar',
        help_text='Período (mes/año inicio-fin) y actividad durante ese tiempo'
    )
    actividades_tiempo_libre = models.TextField(
        blank=True,
        verbose_name='Actividades en tiempo libre',
        help_text='Tipo de actividad, frecuencia y tiempo dedicado'
    )

    # Campos de auditoría
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Personas"
        indexes = [
            models.Index(fields=['folio']),
            models.Index(fields=['curp']),
            models.Index(fields=['apellido_paterno', 'apellido_materno', 'nombre']),
        ]

    def save(self, *args, **kwargs):
        # Normalizar nombres a Title Case
        if self.nombre:
            self.nombre = self.nombre.strip().title()
        if self.apellido_paterno:
            self.apellido_paterno = self.apellido_paterno.strip().title()
        if self.apellido_materno:
            self.apellido_materno = self.apellido_materno.strip().title()

        if not self.folio:
            # Generar folio único: AÑO-MES-SECUENCIA
            year = timezone.now().strftime('%Y')
            month = timezone.now().strftime('%m')
            last_study = Persona.objects.filter(
                folio__startswith=f'{year}{month}'
            ).order_by('-folio').first()

            if last_study:
                last_sequence = int(last_study.folio[-4:])
                new_sequence = str(last_sequence + 1).zfill(4)
            else:
                new_sequence = '0001'

            self.folio = f'{year}{month}{new_sequence}'

        super().save(*args, **kwargs)

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}".strip()

    def __str__(self):
        return f"{self.folio} - {self.nombre_completo}"


class SaludPersona(TimestampModel):
    """Información de salud de la persona evaluada"""
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, related_name='salud')

    NIVEL_SALUD = [
        ('EXC', 'Excelente'),
        ('BUE', 'Buena'),
        ('REG', 'Regular'),
        ('MAL', 'Mala'),
    ]
    nivel_salud = models.CharField(
        max_length=3, choices=NIVEL_SALUD, blank=True,
        verbose_name='Estado de salud general'
    )
    enfermedades_cronicas = models.TextField(
        blank=True,
        verbose_name='Enfermedades crónicas / condiciones médicas / alergias / discapacidad',
        help_text='Especificar enfermedad y tratamiento que lleva'
    )
    antecedentes_familiares = models.TextField(
        blank=True,
        verbose_name='Antecedentes de enfermedades familiares',
        help_text='Enfermedades y familiar(es) que las han padecido'
    )
    consumo_sustancias = models.TextField(
        blank=True,
        verbose_name='Consumo de sustancias',
        help_text='Bebidas alcohólicas, tabaco, medicamentos sin prescripción, estupefacientes u otros; indicar frecuencia'
    )

    class Meta:
        verbose_name = "Salud de persona"
        verbose_name_plural = "Salud de personas"

    def __str__(self):
        return f"Salud de {self.persona.nombre_completo}"
