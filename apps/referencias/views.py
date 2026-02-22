from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import Referencia


class ReferenciaListView(LoginRequiredMixin, ListView):
    model = Referencia
    context_object_name = 'referencias'
    paginate_by = 25


class ReferenciaDetailView(LoginRequiredMixin, DetailView):
    model = Referencia
    context_object_name = 'referencia'


class ReferenciaCreateView(LoginRequiredMixin, CreateView):
    model = Referencia
    fields = [
        'persona', 'tipo', 'nombre', 'telefono', 'email',
        'parentesco_o_relacion', 'tiempo_conocer_anios', 'domicilio',
        'actividad_tiempo_libre', 'lugares_laborado', 'conducta', 'cualidades',
        'verificada', 'comentarios_verificacion',
    ]
    success_url = reverse_lazy('referencias:referencia_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class ReferenciaUpdateView(LoginRequiredMixin, UpdateView):
    model = Referencia
    fields = [
        'persona', 'tipo', 'nombre', 'telefono', 'email',
        'parentesco_o_relacion', 'tiempo_conocer_anios', 'domicilio',
        'actividad_tiempo_libre', 'lugares_laborado', 'conducta', 'cualidades',
        'verificada', 'comentarios_verificacion',
    ]
    success_url = reverse_lazy('referencias:referencia_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class ReferenciaDeleteView(LoginRequiredMixin, DeleteView):
    model = Referencia
    context_object_name = 'referencia'
    success_url = reverse_lazy('referencias:referencia_list')
