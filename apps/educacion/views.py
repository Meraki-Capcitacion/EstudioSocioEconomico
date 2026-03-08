from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import NivelEducativo, Educacion, Idioma


# --- NivelEducativo ---

class NivelEducativoListView(LoginRequiredMixin, ListView):
    model = NivelEducativo
    context_object_name = 'niveles_educativos'
    paginate_by = 25


class NivelEducativoDetailView(LoginRequiredMixin, DetailView):
    model = NivelEducativo
    context_object_name = 'nivel_educativo'


class NivelEducativoCreateView(LoginRequiredMixin, CreateView):
    model = NivelEducativo
    fields = ['nivel', 'orden', 'activo']
    success_url = reverse_lazy('educacion:niveleducativo_list')


class NivelEducativoUpdateView(LoginRequiredMixin, UpdateView):
    model = NivelEducativo
    fields = ['nivel', 'orden', 'activo']
    success_url = reverse_lazy('educacion:niveleducativo_list')


class NivelEducativoDeleteView(LoginRequiredMixin, DeleteView):
    model = NivelEducativo
    context_object_name = 'nivel_educativo'
    success_url = reverse_lazy('educacion:niveleducativo_list')


# --- Educacion ---

class EducacionListView(LoginRequiredMixin, ListView):
    model = Educacion
    context_object_name = 'educaciones'
    paginate_by = 25


class EducacionDetailView(LoginRequiredMixin, DetailView):
    model = Educacion
    context_object_name = 'educacion'


class EducacionCreateView(LoginRequiredMixin, CreateView):
    model = Educacion
    fields = [
        'persona', 'nivel', 'institucion', 'ciudad_institucion',
        'titulo', 'estado', 'anio_inicio', 'anio_fin',
        'tipo_documento_estudio', 'tiene_cedula', 'numero_cedula',
        'documento_verificado',
    ]
    success_url = reverse_lazy('educacion:educacion_list')

    def get_initial(self):
        initial = super().get_initial()
        persona_pk = self.request.GET.get('persona')
        if persona_pk:
            initial['persona'] = persona_pk
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


class EducacionUpdateView(LoginRequiredMixin, UpdateView):
    model = Educacion
    fields = [
        'persona', 'nivel', 'institucion', 'ciudad_institucion',
        'titulo', 'estado', 'anio_inicio', 'anio_fin',
        'tipo_documento_estudio', 'tiene_cedula', 'numero_cedula',
        'documento_verificado',
    ]
    success_url = reverse_lazy('educacion:educacion_list')

    def get_success_url(self):
        back = self.request.GET.get('back')
        if back:
            return reverse_lazy('estudios:estudio_detail', kwargs={'pk': back})
        return super().get_success_url()

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class EducacionDeleteView(LoginRequiredMixin, DeleteView):
    model = Educacion
    context_object_name = 'educacion'
    success_url = reverse_lazy('educacion:educacion_list')


# --- Idioma ---

class IdiomaListView(LoginRequiredMixin, ListView):
    model = Idioma
    context_object_name = 'idiomas'
    paginate_by = 25


class IdiomaDetailView(LoginRequiredMixin, DetailView):
    model = Idioma
    context_object_name = 'idioma'


class IdiomaCreateView(LoginRequiredMixin, CreateView):
    model = Idioma
    fields = [
        'persona', 'idioma',
        'porcentaje_habla', 'porcentaje_escribe', 'porcentaje_lee',
        'plantel', 'periodo_inicio', 'periodo_fin',
        'tiene_certificacion', 'tipo_certificacion', 'nivel_certificacion',
    ]
    success_url = reverse_lazy('educacion:idioma_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class IdiomaUpdateView(LoginRequiredMixin, UpdateView):
    model = Idioma
    fields = [
        'persona', 'idioma',
        'porcentaje_habla', 'porcentaje_escribe', 'porcentaje_lee',
        'plantel', 'periodo_inicio', 'periodo_fin',
        'tiene_certificacion', 'tipo_certificacion', 'nivel_certificacion',
    ]
    success_url = reverse_lazy('educacion:idioma_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class IdiomaDeleteView(LoginRequiredMixin, DeleteView):
    model = Idioma
    context_object_name = 'idioma'
    success_url = reverse_lazy('educacion:idioma_list')
