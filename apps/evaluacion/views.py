from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import EvaluacionRiesgo


class EvaluacionRiesgoListView(LoginRequiredMixin, ListView):
    model = EvaluacionRiesgo
    context_object_name = 'evaluaciones'
    paginate_by = 25


class EvaluacionRiesgoDetailView(LoginRequiredMixin, DetailView):
    model = EvaluacionRiesgo
    context_object_name = 'evaluacion'


class EvaluacionRiesgoCreateView(LoginRequiredMixin, CreateView):
    model = EvaluacionRiesgo
    fields = [
        'estudio', 'evaluador',
        'puntuacion_identificacion', 'puntuacion_domicilio',
        'puntuacion_laboral', 'puntuacion_economica',
        'puntuacion_crediticia', 'puntuacion_referencias',
        'score_final', 'nivel_riesgo',
        'factores_riesgo', 'factores_atenuantes', 'recomendacion_final',
    ]
    success_url = reverse_lazy('evaluacion:evaluacionriesgo_list')

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


class EvaluacionRiesgoUpdateView(LoginRequiredMixin, UpdateView):
    model = EvaluacionRiesgo
    fields = [
        'estudio', 'evaluador',
        'puntuacion_identificacion', 'puntuacion_domicilio',
        'puntuacion_laboral', 'puntuacion_economica',
        'puntuacion_crediticia', 'puntuacion_referencias',
        'score_final', 'nivel_riesgo',
        'factores_riesgo', 'factores_atenuantes', 'recomendacion_final',
    ]
    success_url = reverse_lazy('evaluacion:evaluacionriesgo_list')

    def get_success_url(self):
        back = self.request.GET.get('back')
        if back:
            return reverse_lazy('estudios:estudio_detail', kwargs={'pk': back})
        return super().get_success_url()

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class EvaluacionRiesgoDeleteView(LoginRequiredMixin, DeleteView):
    model = EvaluacionRiesgo
    context_object_name = 'evaluacion'
    success_url = reverse_lazy('evaluacion:evaluacionriesgo_list')
