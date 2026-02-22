from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import GrupoFamiliar


class GrupoFamiliarListView(LoginRequiredMixin, ListView):
    model = GrupoFamiliar
    context_object_name = 'grupos_familiares'
    paginate_by = 25


class GrupoFamiliarDetailView(LoginRequiredMixin, DetailView):
    model = GrupoFamiliar
    context_object_name = 'grupo_familiar'


class GrupoFamiliarCreateView(LoginRequiredMixin, CreateView):
    model = GrupoFamiliar
    fields = [
        'persona', 'nombre_completo', 'parentesco', 'edad',
        'tipo_dependencia', 'ocupacion', 'escolaridad',
        'vive_en_domicilio', 'aporta_ingreso', 'monto_aportacion',
        'telefono', 'ciudad_residencia',
    ]
    success_url = reverse_lazy('familia:grupofamiliar_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class GrupoFamiliarUpdateView(LoginRequiredMixin, UpdateView):
    model = GrupoFamiliar
    fields = [
        'persona', 'nombre_completo', 'parentesco', 'edad',
        'tipo_dependencia', 'ocupacion', 'escolaridad',
        'vive_en_domicilio', 'aporta_ingreso', 'monto_aportacion',
        'telefono', 'ciudad_residencia',
    ]
    success_url = reverse_lazy('familia:grupofamiliar_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class GrupoFamiliarDeleteView(LoginRequiredMixin, DeleteView):
    model = GrupoFamiliar
    context_object_name = 'grupo_familiar'
    success_url = reverse_lazy('familia:grupofamiliar_list')
