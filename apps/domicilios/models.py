from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.configuracion.models import TimestampModel
from apps.personas.models import Persona


class Domicilio(TimestampModel):
    """Modelo de domicilio - Una persona puede tener múltiples domicilios"""
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='domicilios')

    TIPO_DOMICILIO = [
        ('ACT', 'Actual'),
        ('ANT', 'Anterior'),
        ('REF', 'Referencia'),
    ]
    tipo = models.CharField(max_length=3, choices=TIPO_DOMICILIO, default='ACT')

    # Dirección
    calle = models.CharField(max_length=200)
    numero_exterior = models.CharField(max_length=20)
    numero_interior = models.CharField(max_length=20, blank=True)
    entre_calles = models.CharField(max_length=200, blank=True)
    colonia = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=5)
    municipio = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    pais = models.CharField(max_length=100, default='México')

    # Características de la vivienda
    TIPO_VIVIENDA = [
        ('PRO', 'Propia'),
        ('PROHIP', 'Propia con hipoteca'),
        ('REN', 'Rentada'),
        ('PRE', 'Prestada'),
        ('FAM', 'Familiar'),
        ('OTR', 'Otro'),
    ]
    tipo_vivienda = models.CharField(max_length=6, choices=TIPO_VIVIENDA, blank=True)

    TIPO_INMUEBLE = [
        ('CAS', 'Casa'),
        ('DEP', 'Departamento'),
    ]
    tipo_inmueble = models.CharField(
        max_length=3, choices=TIPO_INMUEBLE, blank=True,
        verbose_name='Tipo de inmueble'
    )

    propietario_nombre = models.CharField(
        max_length=200, blank=True,
        verbose_name='Nombre del propietario / A nombre de quién está el domicilio'
    )

    # Características físicas
    material_construccion = models.CharField(max_length=100, blank=True)
    numero_habitaciones = models.IntegerField(
        validators=[MinValueValidator(1)], null=True, blank=True
    )
    numero_niveles = models.IntegerField(default=1)

    superficie_m2 = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name='Superficie aproximada (m²)'
    )

    # Valor del inmueble y bienes
    valor_inmueble = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        verbose_name='Valor aproximado del inmueble'
    )

    RANGO_VALOR = [
        ('R1', '$1,000 - $10,000'),
        ('R2', '$10,000 - $20,000'),
        ('R3', '$20,000 - $50,000'),
        ('R4', 'Más de $50,000'),
    ]
    valor_muebles = models.CharField(
        max_length=2, choices=RANGO_VALOR, blank=True,
        verbose_name='Valor aproximado de muebles'
    )
    valor_electrodomesticos = models.CharField(
        max_length=2, choices=RANGO_VALOR, blank=True,
        verbose_name='Valor aproximado de electrodomésticos'
    )

    # Servicios
    tiene_agua = models.BooleanField(default=False, verbose_name='Agua')
    tiene_luz = models.BooleanField(default=False, verbose_name='Luz')
    tiene_drenaje = models.BooleanField(default=False, verbose_name='Drenaje / Alcantarillado')
    tiene_gas = models.BooleanField(default=False, verbose_name='Gas')
    tiene_internet = models.BooleanField(default=False, verbose_name='Internet')
    tiene_tv_cable = models.BooleanField(default=False, verbose_name='TV de paga / Cable')
    tiene_pavimentacion = models.BooleanField(default=False, verbose_name='Pavimentación')
    tiene_telefono_domicilio = models.BooleanField(default=False, verbose_name='Teléfono fijo en el domicilio')

    # Espacios del inmueble
    tiene_sala = models.BooleanField(default=False, verbose_name='Sala')
    tiene_cocina = models.BooleanField(default=False, verbose_name='Cocina')
    tiene_comedor = models.BooleanField(default=False, verbose_name='Comedor')
    tiene_patio_servicio = models.BooleanField(default=False, verbose_name='Patio de servicio')
    tiene_cochera = models.BooleanField(default=False, verbose_name='Cochera')

    # Materiales de construcción
    tiene_piso = models.BooleanField(default=False, verbose_name='Piso (mosaico/madera/porcelanato)')
    tiene_piso_cemento = models.BooleanField(default=False, verbose_name='Piso de cemento')
    tiene_enjarre = models.BooleanField(default=False, verbose_name='Enjarre en las paredes')
    tiene_paredes_sin_enjarre = models.BooleanField(default=False, verbose_name='Paredes sin enjarre')
    tiene_techo_lamina = models.BooleanField(default=False, verbose_name='Techo de lámina')
    tiene_loza = models.BooleanField(default=False, verbose_name='Loza')
    tiene_puertas = models.BooleanField(default=False, verbose_name='Puertas')

    # Condición general
    ORDEN_LIMPIEZA = [
        ('BUE', 'Bueno'),
        ('REG', 'Regular'),
        ('MAL', 'Malo'),
    ]
    orden_limpieza = models.CharField(
        max_length=3, choices=ORDEN_LIMPIEZA, blank=True,
        verbose_name='Orden, mantenimiento y limpieza del inmueble'
    )

    observaciones_inmueble = models.TextField(
        blank=True,
        verbose_name='Observaciones del inmueble'
    )

    # Tiempo de residencia
    tiempo_residencia_anios = models.IntegerField(
        validators=[MinValueValidator(0)], null=True, blank=True
    )
    tiempo_residencia_meses = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(11)], null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "Domicilios"

    def __str__(self):
        return f"{self.calle} #{self.numero_exterior}, {self.colonia}"
