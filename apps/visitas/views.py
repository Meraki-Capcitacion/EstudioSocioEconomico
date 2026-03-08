from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import VisitaDomiciliaria


class VisitaDomiciliariaListView(LoginRequiredMixin, ListView):
    model = VisitaDomiciliaria
    context_object_name = 'visitas'
    paginate_by = 25


class VisitaDomiciliariaDetailView(LoginRequiredMixin, DetailView):
    model = VisitaDomiciliaria
    context_object_name = 'visita'


class VisitaDomiciliariaCreateView(LoginRequiredMixin, CreateView):
    model = VisitaDomiciliaria
    template_name = 'visitas/visitadomiciliaria_reporte_form.html'
    fields = [
        'estudio', 'evaluador', 'fecha_visita',
        'latitud', 'longitud',
        'persona_encontrada', 'verificacion_domicilio',
        'tipo_zona', 'nivel_seguridad', 'nivel_ruido', 'acceso_transporte',
        'observaciones_generales', 'comentarios_colonos', 'recomendacion',
    ]
    success_url = reverse_lazy('visitas:visitadomiciliaria_list')

    def get_initial(self):
        initial = super().get_initial()
        estudio_pk = self.request.GET.get('estudio')
        if estudio_pk:
            initial['estudio'] = estudio_pk
        return initial

    def get_success_url(self):
        back = self.request.GET.get('back')
        if back:
            return reverse_lazy('estudios:estudio_detail', kwargs={'pk': back})
        return super().get_success_url()

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class VisitaDomiciliariaUpdateView(LoginRequiredMixin, UpdateView):
    model = VisitaDomiciliaria
    template_name = 'visitas/visitadomiciliaria_reporte_form.html'
    fields = [
        'estudio', 'evaluador', 'fecha_visita',
        'latitud', 'longitud',
        'persona_encontrada', 'verificacion_domicilio',
        'tipo_zona', 'nivel_seguridad', 'nivel_ruido', 'acceso_transporte',
        'observaciones_generales', 'comentarios_colonos', 'recomendacion',
    ]
    success_url = reverse_lazy('visitas:visitadomiciliaria_list')

    def get_success_url(self):
        back = self.request.GET.get('back')
        if back:
            return reverse_lazy('estudios:estudio_detail', kwargs={'pk': back})
        return super().get_success_url()

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class VisitaDomiciliariaDeleteView(LoginRequiredMixin, DeleteView):
    model = VisitaDomiciliaria
    context_object_name = 'visita'
    success_url = reverse_lazy('visitas:visitadomiciliaria_list')


class AgendaInspectorView(LoginRequiredMixin, ListView):
    """Agenda de visitas asignadas al inspector actual (Fase 4)."""
    model = VisitaDomiciliaria
    template_name = 'visitas/agenda.html'
    context_object_name = 'visitas'

    def get_queryset(self):
        return (
            VisitaDomiciliaria.objects
            .filter(evaluador=self.request.user)
            .select_related('estudio__persona')
            .order_by('fecha_visita')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoy = timezone.now().date()
        visitas = ctx['visitas']
        ctx['visitas_hoy'] = [v for v in visitas if v.fecha_visita.date() == hoy]
        ctx['visitas_proximas'] = [v for v in visitas if v.fecha_visita.date() > hoy]
        ctx['visitas_pasadas'] = [v for v in visitas if v.fecha_visita.date() < hoy]
        return ctx
