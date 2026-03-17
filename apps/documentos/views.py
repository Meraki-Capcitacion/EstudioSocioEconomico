from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import Documento
from .forms import DocumentoForm
from apps.estudios.models import EstudioSocioeconomico


class DocumentoListView(LoginRequiredMixin, ListView):
    model = Documento
    context_object_name = 'documentos'
    paginate_by = 25

    def get_queryset(self):
        from django.db.models import Q
        qs = super().get_queryset().select_related('persona', 'estudio')
        tipo = self.request.GET.get('tipo', '')
        verificado = self.request.GET.get('verificado', '')
        q = self.request.GET.get('q', '').strip()
        if tipo:
            qs = qs.filter(tipo=tipo)
        if verificado == '1':
            qs = qs.filter(verificado=True)
        elif verificado == '0':
            qs = qs.filter(verificado=False)
        if q:
            qs = qs.filter(
                Q(persona__nombre__icontains=q) |
                Q(persona__apellido_paterno__icontains=q) |
                Q(persona__apellido_materno__icontains=q) |
                Q(persona__rfc__icontains=q) |
                Q(persona__curp__icontains=q) |
                Q(nombre_archivo__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tipos_documento'] = Documento.TIPO_DOCUMENTO
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class DocumentoDetailView(LoginRequiredMixin, DetailView):
    model = Documento
    context_object_name = 'documento'


class EstudiosPorPersonaView(LoginRequiredMixin, View):
    """Retorna las opciones <option> de estudios filtradas por persona (para HTMX)."""

    def get(self, request):
        persona_id = request.GET.get('persona')
        estudios = EstudioSocioeconomico.objects.none()
        if persona_id:
            estudios = EstudioSocioeconomico.objects.filter(persona_id=persona_id)
        options = '<option value="">---------</option>'
        for estudio in estudios:
            options += f'<option value="{estudio.pk}">{estudio}</option>'
        return HttpResponse(options)


class DocumentoCreateView(LoginRequiredMixin, CreateView):
    model = Documento
    form_class = DocumentoForm
    success_url = reverse_lazy('documentos:documento_list')

    def get_initial(self):
        initial = super().get_initial()
        persona_pk = self.request.GET.get('persona')
        estudio_pk = self.request.GET.get('estudio')
        if persona_pk:
            initial['persona'] = persona_pk
        if estudio_pk:
            initial['estudio'] = estudio_pk
        return initial

    def get_success_url(self):
        back = self.request.GET.get('back')
        if back:
            return reverse_lazy('estudios:estudio_detail', kwargs={'pk': back})
        return super().get_success_url()

    def form_valid(self, form):
        archivo = form.cleaned_data.get('archivo')
        if archivo:
            form.instance.tamaño = archivo.size
            if not form.cleaned_data.get('nombre_archivo'):
                form.instance.nombre_archivo = archivo.name
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class DocumentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Documento
    form_class = DocumentoForm
    success_url = reverse_lazy('documentos:documento_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class DocumentoDeleteView(LoginRequiredMixin, DeleteView):
    model = Documento
    context_object_name = 'documento'
    success_url = reverse_lazy('documentos:documento_list')
