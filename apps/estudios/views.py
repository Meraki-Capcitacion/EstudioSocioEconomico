from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import EstudioSocioeconomico


class EstudioListView(LoginRequiredMixin, ListView):
    model = EstudioSocioeconomico
    context_object_name = 'estudios'
    paginate_by = 25


class EstudioDetailView(LoginRequiredMixin, DetailView):
    model = EstudioSocioeconomico
    context_object_name = 'estudio'


class EstudioCreateView(LoginRequiredMixin, CreateView):
    model = EstudioSocioeconomico
    fields = [
        'persona', 'empresa_cliente', 'tipo_estudio', 'estado',
        'fecha_programada_visita', 'fecha_realizacion', 'fecha_aprobacion',
        'observaciones', 'conclusion', 'aspectos_positivos', 'aspectos_negativos',
        'expectativas_salariales', 'medio_enterado_vacante',
        'tiempo_traslado', 'comentarios_adicionales',
    ]
    success_url = reverse_lazy('estudios:estudio_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class EstudioUpdateView(LoginRequiredMixin, UpdateView):
    model = EstudioSocioeconomico
    fields = [
        'persona', 'empresa_cliente', 'tipo_estudio', 'estado',
        'fecha_programada_visita', 'fecha_realizacion', 'fecha_aprobacion',
        'observaciones', 'conclusion', 'aspectos_positivos', 'aspectos_negativos',
        'expectativas_salariales', 'medio_enterado_vacante',
        'tiempo_traslado', 'comentarios_adicionales',
    ]
    success_url = reverse_lazy('estudios:estudio_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class EstudioDeleteView(LoginRequiredMixin, DeleteView):
    model = EstudioSocioeconomico
    context_object_name = 'estudio'
    success_url = reverse_lazy('estudios:estudio_list')
