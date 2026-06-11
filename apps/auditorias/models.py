from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class RegistroAuditoria(models.Model):
    ACCIONES = [
        ('CRE', 'Creó'),
        ('MOD', 'Modificó'),
        ('ELI', 'Eliminó'),
        ('CAM', 'Cambió estado'),
        ('VER', 'Verificó'),
    ]

    usuario     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='auditorias', verbose_name='Usuario')
    accion      = models.CharField(max_length=3, choices=ACCIONES, verbose_name='Acción')
    modelo      = models.CharField(max_length=100, verbose_name='Modelo')
    objeto_id   = models.PositiveIntegerField(verbose_name='ID del objeto')
    descripcion = models.TextField(verbose_name='Descripción')
    datos_antes  = models.JSONField(null=True, blank=True, verbose_name='Datos antes')
    datos_despues = models.JSONField(null=True, blank=True, verbose_name='Datos después')
    ip_address  = models.GenericIPAddressField(null=True, blank=True, verbose_name='Dirección IP')
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Registro de auditoría'
        verbose_name_plural = 'Registros de auditoría'
        indexes = [
            models.Index(fields=['modelo', 'objeto_id']),
            models.Index(fields=['usuario']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        usuario_str = self.usuario.get_full_name() or self.usuario.username if self.usuario else 'Sistema'
        return f'{usuario_str} — {self.get_accion_display()} {self.modelo} #{self.objeto_id}'
