from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import HistorialLaboral


class HistorialLaboralListView(LoginRequiredMixin, ListView):
    model = HistorialLaboral
    context_object_name = 'historiales_laborales'
    paginate_by = 25


class HistorialLaboralDetailView(LoginRequiredMixin, DetailView):
    model = HistorialLaboral
    context_object_name = 'historial_laboral'


class HistorialLaboralCreateView(LoginRequiredMixin, CreateView):
    model = HistorialLaboral
    fields = [
        'persona', 'empresa', 'puesto', 'telefono_empresa',
        'fecha_inicio', 'fecha_fin', 'es_trabajo_actual',
        'salario_inicial', 'salario_final',
        'nombre_jefe', 'telefono_jefe', 'motivo_separacion',
        'verificada', 'fecha_verificacion',
    ]
    success_url = reverse_lazy('laboral:historiallaboral_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class HistorialLaboralUpdateView(LoginRequiredMixin, UpdateView):
    model = HistorialLaboral
    fields = [
        'persona', 'empresa', 'puesto', 'telefono_empresa',
        'fecha_inicio', 'fecha_fin', 'es_trabajo_actual',
        'salario_inicial', 'salario_final',
        'nombre_jefe', 'telefono_jefe', 'motivo_separacion',
        'verificada', 'fecha_verificacion',
    ]
    success_url = reverse_lazy('laboral:historiallaboral_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class HistorialLaboralDeleteView(LoginRequiredMixin, DeleteView):
    model = HistorialLaboral
    context_object_name = 'historial_laboral'
    success_url = reverse_lazy('laboral:historiallaboral_list')
