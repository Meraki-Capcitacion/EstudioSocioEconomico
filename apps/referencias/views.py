from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .forms import ReferenciaForm
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
    form_class = ReferenciaForm
    success_url = reverse_lazy('referencias:referencia_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class ReferenciaUpdateView(LoginRequiredMixin, UpdateView):
    model = Referencia
    form_class = ReferenciaForm
    success_url = reverse_lazy('referencias:referencia_list')

    def get_success_url(self):
        back = self.request.GET.get('back')
        if back:
            return reverse_lazy('estudios:estudio_detail', kwargs={'pk': back})
        return super().get_success_url()

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class ReferenciaDeleteView(LoginRequiredMixin, DeleteView):
    model = Referencia
    context_object_name = 'referencia'
    success_url = reverse_lazy('referencias:referencia_list')


class VerificarReferenciaView(LoginRequiredMixin, View):
    """Formulario de verificación telefónica de una referencia (Fase 4 — Inspector)."""

    template_name = 'referencias/referencia_verificar_form.html'

    def get(self, request, pk):
        from django.shortcuts import render
        referencia = get_object_or_404(Referencia, pk=pk)
        return render(request, self.template_name, {'referencia': referencia})

    def post(self, request, pk):
        referencia = get_object_or_404(Referencia, pk=pk)
        referencia.actividad_tiempo_libre = request.POST.get('actividad_tiempo_libre', referencia.actividad_tiempo_libre)
        referencia.lugares_laborado = request.POST.get('lugares_laborado', referencia.lugares_laborado)
        referencia.conducta = request.POST.get('conducta', referencia.conducta)
        referencia.cualidades = request.POST.get('cualidades', referencia.cualidades)
        referencia.comentarios_verificacion = request.POST.get('comentarios_verificacion', referencia.comentarios_verificacion)
        referencia.verificada = True
        referencia.fecha_verificacion = timezone.now()
        referencia.updated_by = request.user
        referencia.save()
        messages.success(request, f'Referencia de {referencia.nombre} marcada como verificada.')

        back = request.GET.get('back')
        if back:
            return redirect('estudios:estudio_detail', pk=back)
        return redirect('referencias:referencia_list')
