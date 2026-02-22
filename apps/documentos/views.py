from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import Documento


class DocumentoListView(LoginRequiredMixin, ListView):
    model = Documento
    context_object_name = 'documentos'
    paginate_by = 25


class DocumentoDetailView(LoginRequiredMixin, DetailView):
    model = Documento
    context_object_name = 'documento'


class DocumentoCreateView(LoginRequiredMixin, CreateView):
    model = Documento
    fields = [
        'persona', 'estudio', 'tipo',
        'archivo', 'nombre_archivo',
        'verificado', 'verificado_por',
    ]
    success_url = reverse_lazy('documentos:documento_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class DocumentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Documento
    fields = [
        'persona', 'estudio', 'tipo',
        'archivo', 'nombre_archivo',
        'verificado', 'verificado_por',
    ]
    success_url = reverse_lazy('documentos:documento_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class DocumentoDeleteView(LoginRequiredMixin, DeleteView):
    model = Documento
    context_object_name = 'documento'
    success_url = reverse_lazy('documentos:documento_list')
