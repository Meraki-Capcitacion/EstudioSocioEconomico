from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import EstudioSocioeconomico


TRANSICIONES_VALIDAS = {
    'BOR': ['VIS', 'CAN'],
    'VIS': ['PRO', 'CAN'],
    'PRO': ['COM', 'CAN'],
    'COM': ['REV'],
    'REV': ['APR', 'REC'],
    'APR': [],
    'REC': ['BOR'],
    'CAN': [],
}


class EstudioListView(LoginRequiredMixin, ListView):
    model = EstudioSocioeconomico
    context_object_name = 'estudios'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '')
        estado = self.request.GET.get('estado', '')
        if q:
            qs = qs.filter(
                Q(persona__nombre__icontains=q) | Q(persona__apellido_paterno__icontains=q) |
                Q(persona__folio__icontains=q)
            )
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['estado_filtro'] = self.request.GET.get('estado', '')
        ctx['estados'] = EstudioSocioeconomico.ESTADO_ESTUDIO
        return ctx


class EstudioDetailView(LoginRequiredMixin, DetailView):
    model = EstudioSocioeconomico
    context_object_name = 'estudio'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        estudio = self.get_object()
        ctx['transiciones_validas'] = TRANSICIONES_VALIDAS.get(estudio.estado, [])
        ctx['estados_display'] = dict(EstudioSocioeconomico.ESTADO_ESTUDIO)
        return ctx


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


class CambiarEstadoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        estudio = get_object_or_404(EstudioSocioeconomico, pk=pk)
        nuevo_estado = request.POST.get('estado')
        observacion = request.POST.get('observacion', '')
        estados_validos = TRANSICIONES_VALIDAS.get(estudio.estado, [])
        if nuevo_estado in estados_validos:
            estudio.estado = nuevo_estado
            if observacion:
                estudio.observaciones = observacion
            estudio.updated_by = request.user
            estudio.save()
            messages.success(request, f'Estado actualizado a {estudio.get_estado_display()}')
        else:
            messages.error(request, 'Transición de estado no válida')
        return redirect('estudios:estudio_detail', pk=pk)
