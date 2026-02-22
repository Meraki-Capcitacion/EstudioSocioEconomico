from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import SituacionEconomica


class SituacionEconomicaListView(LoginRequiredMixin, ListView):
    model = SituacionEconomica
    context_object_name = 'situaciones_economicas'
    paginate_by = 25


class SituacionEconomicaDetailView(LoginRequiredMixin, DetailView):
    model = SituacionEconomica
    context_object_name = 'situacion_economica'


class SituacionEconomicaCreateView(LoginRequiredMixin, CreateView):
    model = SituacionEconomica
    fields = [
        'estudio', 'situacion_economica_percibida',
        'salario_mensual', 'bonos_comisiones', 'ingresos_extra',
        'apoyo_familiar', 'otros_ingresos', 'descripcion_otros_ingresos',
        'gasto_alimentacion', 'gasto_vivienda', 'gasto_servicios',
        'gasto_transporte', 'gasto_educacion', 'gasto_salud',
        'gasto_deudas', 'otros_gastos', 'descripcion_otros_gastos',
        'tiene_automovil', 'automovil_marca_modelo', 'automovil_anio',
        'automovil_valor_comercial', 'automovil_con_adeudo',
        'patrimonio_inmobiliario', 'descripcion_patrimonio',
        'institucion_bancaria', 'afore',
        'tiene_creditos', 'credito_hipotecario', 'credito_automotriz',
        'tarjetas_credito', 'tarjeta_credito_banco',
        'tienda_departamental_nombre', 'tienda_departamental_adeudo',
        'prestamos_personales', 'otros_creditos', 'descripcion_otros_creditos',
    ]
    success_url = reverse_lazy('economia:situacioneconomica_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class SituacionEconomicaUpdateView(LoginRequiredMixin, UpdateView):
    model = SituacionEconomica
    fields = [
        'estudio', 'situacion_economica_percibida',
        'salario_mensual', 'bonos_comisiones', 'ingresos_extra',
        'apoyo_familiar', 'otros_ingresos', 'descripcion_otros_ingresos',
        'gasto_alimentacion', 'gasto_vivienda', 'gasto_servicios',
        'gasto_transporte', 'gasto_educacion', 'gasto_salud',
        'gasto_deudas', 'otros_gastos', 'descripcion_otros_gastos',
        'tiene_automovil', 'automovil_marca_modelo', 'automovil_anio',
        'automovil_valor_comercial', 'automovil_con_adeudo',
        'patrimonio_inmobiliario', 'descripcion_patrimonio',
        'institucion_bancaria', 'afore',
        'tiene_creditos', 'credito_hipotecario', 'credito_automotriz',
        'tarjetas_credito', 'tarjeta_credito_banco',
        'tienda_departamental_nombre', 'tienda_departamental_adeudo',
        'prestamos_personales', 'otros_creditos', 'descripcion_otros_creditos',
    ]
    success_url = reverse_lazy('economia:situacioneconomica_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class SituacionEconomicaDeleteView(LoginRequiredMixin, DeleteView):
    model = SituacionEconomica
    context_object_name = 'situacion_economica'
    success_url = reverse_lazy('economia:situacioneconomica_list')
