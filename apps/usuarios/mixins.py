"""
Mixins de control de acceso basado en roles (ANA / INS / AUD).

Uso en vistas:
    class MiVistaPrivada(AnalistaRequeridoMixin, DetailView):
        ...
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class RolRequeridoMixin(LoginRequiredMixin):
    """
    Mixin base. Subclases deben definir `roles_permitidos` como
    lista/tupla de códigos de rol, p.ej. ['ANA'] o ['ANA', 'INS'].
    """
    roles_permitidos = []

    def dispatch(self, request, *args, **kwargs):
        respuesta = super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return respuesta

        # Superusuarios siempre tienen acceso
        if request.user.is_superuser:
            return respuesta

        try:
            perfil = request.user.perfil
        except Exception:
            raise PermissionDenied

        if not perfil.activo:
            raise PermissionDenied

        if perfil.rol not in self.roles_permitidos:
            raise PermissionDenied

        return respuesta


class AnalistaRequeridoMixin(RolRequeridoMixin):
    """Solo analistas (ANA) pueden acceder."""
    roles_permitidos = ['ANA']


class InspectorRequeridoMixin(RolRequeridoMixin):
    """Analistas e inspectores pueden acceder."""
    roles_permitidos = ['ANA', 'INS']


class AuditorRequeridoMixin(RolRequeridoMixin):
    """Analistas y auditores pueden acceder."""
    roles_permitidos = ['ANA', 'AUD']


class SuperusuarioRequeridoMixin(LoginRequiredMixin):
    """Solo superusuarios pueden acceder."""

    def dispatch(self, request, *args, **kwargs):
        respuesta = super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return respuesta
        if not request.user.is_superuser:
            raise PermissionDenied
        return respuesta
