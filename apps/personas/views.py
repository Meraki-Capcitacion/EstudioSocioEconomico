from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import Persona


class PersonaListView(LoginRequiredMixin, ListView):
    model = Persona
    context_object_name = 'personas'
    paginate_by = 25


class PersonaDetailView(LoginRequiredMixin, DetailView):
    model = Persona
    context_object_name = 'persona'


class PersonaCreateView(LoginRequiredMixin, CreateView):
    model = Persona
    fields = [
        'nombre', 'apellido_paterno', 'apellido_materno',
        'fecha_nacimiento', 'lugar_nacimiento',
        'tipo_identificacion', 'numero_identificacion',
        'curp', 'rfc', 'nss',
        'licencia_manejo_folio', 'cartilla_militar_folio', 'acta_nacimiento_numero',
        'email', 'telefono_movil', 'telefono_fijo', 'facebook_perfil',
        'estado_civil', 'numero_dependientes',
        'peso', 'estatura',
        'activo',
    ]
    success_url = reverse_lazy('personas:persona_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class PersonaUpdateView(LoginRequiredMixin, UpdateView):
    model = Persona
    fields = [
        'nombre', 'apellido_paterno', 'apellido_materno',
        'fecha_nacimiento', 'lugar_nacimiento',
        'tipo_identificacion', 'numero_identificacion',
        'curp', 'rfc', 'nss',
        'licencia_manejo_folio', 'cartilla_militar_folio', 'acta_nacimiento_numero',
        'email', 'telefono_movil', 'telefono_fijo', 'facebook_perfil',
        'estado_civil', 'numero_dependientes',
        'peso', 'estatura',
        'activo',
    ]
    success_url = reverse_lazy('personas:persona_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class PersonaDeleteView(LoginRequiredMixin, DeleteView):
    model = Persona
    context_object_name = 'persona'
    success_url = reverse_lazy('personas:persona_list')
