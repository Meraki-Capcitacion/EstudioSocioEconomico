from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView

from .forms import PerfilUsuarioForm
from .mixins import AnalistaRequeridoMixin, SuperusuarioRequeridoMixin
from .models import MODULOS_DISPONIBLES, MODULOS_POR_ROL_DEFAULT, PerfilUsuario, PermisoModulo


class MiPerfilView(LoginRequiredMixin, DetailView):
    """Muestra el perfil del usuario autenticado."""
    template_name = 'usuarios/mi_perfil.html'
    context_object_name = 'perfil'

    def get_object(self, queryset=None):
        perfil, _ = PerfilUsuario.objects.get_or_create(
            usuario=self.request.user,
            defaults={'rol': 'ANA'},
        )
        return perfil


class MiPerfilEditarView(LoginRequiredMixin, UpdateView):
    """Permite al usuario editar su propio perfil (teléfono)."""
    model = PerfilUsuario
    form_class = PerfilUsuarioForm
    template_name = 'usuarios/perfil_form.html'
    success_url = reverse_lazy('usuarios:mi_perfil')

    def get_object(self, queryset=None):
        perfil, _ = PerfilUsuario.objects.get_or_create(
            usuario=self.request.user,
            defaults={'rol': 'ANA'},
        )
        return perfil

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['es_edicion_rol'] = False
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return super().form_valid(form)


class UsuarioListView(AnalistaRequeridoMixin, ListView):
    """Lista de usuarios y sus roles — solo accesible para analistas."""
    model = PerfilUsuario
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'perfiles'
    paginate_by = 25

    def get_queryset(self):
        return PerfilUsuario.objects.select_related('usuario').order_by(
            'usuario__last_name', 'usuario__first_name'
        )


class UsuarioRolEditarView(AnalistaRequeridoMixin, UpdateView):
    """Permite a analistas cambiar el rol de otro usuario."""
    model = PerfilUsuario
    form_class = PerfilUsuarioForm
    template_name = 'usuarios/perfil_form.html'
    success_url = reverse_lazy('usuarios:usuario_list')

    def get_object(self, queryset=None):
        usuario = get_object_or_404(User, pk=self.kwargs['user_pk'])
        perfil, _ = PerfilUsuario.objects.get_or_create(
            usuario=usuario,
            defaults={'rol': 'ANA'},
        )
        return perfil

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['es_edicion_rol'] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Rol del usuario actualizado.')
        return super().form_valid(form)


class PermisosUsuarioView(SuperusuarioRequeridoMixin, View):
    """
    Gestión de permisos de módulo por usuario.
    Solo accesible para superusuarios.
    """
    template_name = 'usuarios/permisos_modulos.html'

    def _get_perfil(self):
        usuario = get_object_or_404(User, pk=self.kwargs['user_pk'])
        perfil, _ = PerfilUsuario.objects.get_or_create(
            usuario=usuario,
            defaults={'rol': 'ANA'},
        )
        return perfil

    def get(self, request, *args, **kwargs):
        perfil = self._get_perfil()
        tiene_personalizados = perfil.usa_permisos_personalizados
        if tiene_personalizados:
            modulos_activos = set(perfil.permisos_modulos.values_list('modulo', flat=True))
        else:
            modulos_activos = MODULOS_POR_ROL_DEFAULT.get(perfil.rol, set())

        context = {
            'perfil': perfil,
            'modulos_disponibles': MODULOS_DISPONIBLES,
            'modulos_activos': modulos_activos,
            'tiene_personalizados': tiene_personalizados,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        perfil = self._get_perfil()
        accion = request.POST.get('accion', 'guardar')

        if accion == 'restablecer':
            perfil.permisos_modulos.all().delete()
            messages.success(
                request,
                f'Permisos de {perfil} restablecidos a los defaults del rol {perfil.get_rol_display()}.',
            )
            return redirect('usuarios:usuario_list')

        # Guardar permisos explícitos
        modulos_validos = {m[0] for m in MODULOS_DISPONIBLES}
        modulos_seleccionados = {
            m for m in request.POST.getlist('modulos') if m in modulos_validos
        }

        perfil.permisos_modulos.all().delete()
        for modulo in modulos_seleccionados:
            PermisoModulo.objects.create(perfil=perfil, modulo=modulo)

        messages.success(
            request,
            f'Permisos de módulo para {perfil} actualizados correctamente.',
        )
        return redirect('usuarios:usuario_list')
