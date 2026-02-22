from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import Domicilio


class DomicilioListView(LoginRequiredMixin, ListView):
    model = Domicilio
    context_object_name = 'domicilios'
    paginate_by = 25


class DomicilioDetailView(LoginRequiredMixin, DetailView):
    model = Domicilio
    context_object_name = 'domicilio'


class DomicilioCreateView(LoginRequiredMixin, CreateView):
    model = Domicilio
    fields = [
        'persona', 'tipo',
        'calle', 'numero_exterior', 'numero_interior', 'entre_calles',
        'colonia', 'codigo_postal', 'municipio', 'estado', 'pais',
        'tipo_vivienda', 'tipo_inmueble', 'propietario_nombre',
        'numero_habitaciones', 'numero_niveles',
        'superficie_m2', 'valor_inmueble', 'valor_muebles', 'valor_electrodomesticos',
        'tiene_agua', 'tiene_luz', 'tiene_drenaje', 'tiene_gas',
        'tiene_internet', 'tiene_tv_cable', 'tiene_pavimentacion', 'tiene_telefono_domicilio',
        'tiene_sala', 'tiene_cocina', 'tiene_comedor', 'tiene_patio_servicio', 'tiene_cochera',
        'tiene_piso', 'tiene_piso_cemento', 'tiene_enjarre', 'tiene_paredes_sin_enjarre',
        'tiene_techo_lamina', 'tiene_loza', 'tiene_puertas',
        'orden_limpieza', 'observaciones_inmueble',
        'tiempo_residencia_anios', 'tiempo_residencia_meses',
    ]
    success_url = reverse_lazy('domicilios:domicilio_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class DomicilioUpdateView(LoginRequiredMixin, UpdateView):
    model = Domicilio
    fields = [
        'persona', 'tipo',
        'calle', 'numero_exterior', 'numero_interior', 'entre_calles',
        'colonia', 'codigo_postal', 'municipio', 'estado', 'pais',
        'tipo_vivienda', 'tipo_inmueble', 'propietario_nombre',
        'numero_habitaciones', 'numero_niveles',
        'superficie_m2', 'valor_inmueble', 'valor_muebles', 'valor_electrodomesticos',
        'tiene_agua', 'tiene_luz', 'tiene_drenaje', 'tiene_gas',
        'tiene_internet', 'tiene_tv_cable', 'tiene_pavimentacion', 'tiene_telefono_domicilio',
        'tiene_sala', 'tiene_cocina', 'tiene_comedor', 'tiene_patio_servicio', 'tiene_cochera',
        'tiene_piso', 'tiene_piso_cemento', 'tiene_enjarre', 'tiene_paredes_sin_enjarre',
        'tiene_techo_lamina', 'tiene_loza', 'tiene_puertas',
        'orden_limpieza', 'observaciones_inmueble',
        'tiempo_residencia_anios', 'tiempo_residencia_meses',
    ]
    success_url = reverse_lazy('domicilios:domicilio_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class DomicilioDeleteView(LoginRequiredMixin, DeleteView):
    model = Domicilio
    context_object_name = 'domicilio'
    success_url = reverse_lazy('domicilios:domicilio_list')
