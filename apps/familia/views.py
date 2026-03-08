from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .forms import GrupoFamiliarForm
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
    form_class = GrupoFamiliarForm
    success_url = reverse_lazy('familia:grupofamiliar_list')

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


class GrupoFamiliarUpdateView(LoginRequiredMixin, UpdateView):
    model = GrupoFamiliar
    form_class = GrupoFamiliarForm
    success_url = reverse_lazy('familia:grupofamiliar_list')

    def get_success_url(self):
        back = self.request.GET.get('back')
        if back:
            return reverse_lazy('estudios:estudio_detail', kwargs={'pk': back})
        return super().get_success_url()

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class GrupoFamiliarDeleteView(LoginRequiredMixin, DeleteView):
    model = GrupoFamiliar
    context_object_name = 'grupo_familiar'
    success_url = reverse_lazy('familia:grupofamiliar_list')
