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

    class Meta:
        verbose_name = "Tipo de estudio"
        verbose_name_plural = "Tipos de estudio"
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre