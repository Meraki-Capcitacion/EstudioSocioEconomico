from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import RegistroAuditoria

User = get_user_model()

MODELOS_AUDITADOS = [
    'Persona',
    'EstudioSocioeconomico',
    'EvaluacionRiesgo',
    'Documento',
    'HistorialLaboral',
    'Referencia',
]


class AuditoriaListView(LoginRequiredMixin, ListView):
    model = RegistroAuditoria
    template_name = 'auditorias/auditoria_list.html'
    context_object_name = 'registros'
    paginate_by = 50

    def get_queryset(self):
        qs = RegistroAuditoria.objects.select_related('usuario')
        modelo = self.request.GET.get('modelo', '').strip()
        accion = self.request.GET.get('accion', '').strip()
        usuario_id = self.request.GET.get('usuario', '').strip()
        fecha_desde = self.request.GET.get('fecha_desde', '').strip()
        fecha_hasta = self.request.GET.get('fecha_hasta', '').strip()

        if modelo:
            qs = qs.filter(modelo=modelo)
        if accion:
            qs = qs.filter(accion=accion)
        if usuario_id:
            qs = qs.filter(usuario_id=usuario_id)
        if fecha_desde:
            qs = qs.filter(created_at__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(created_at__date__lte=fecha_hasta)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['modelos_disponibles'] = MODELOS_AUDITADOS
        ctx['acciones'] = RegistroAuditoria.ACCIONES
        ctx['usuarios'] = User.objects.filter(auditorias__isnull=False).distinct().order_by('username')
        ctx['filtros'] = {
            'modelo': self.request.GET.get('modelo', ''),
            'accion': self.request.GET.get('accion', ''),
            'usuario': self.request.GET.get('usuario', ''),
            'fecha_desde': self.request.GET.get('fecha_desde', ''),
            'fecha_hasta': self.request.GET.get('fecha_hasta', ''),
        }
        return ctx
