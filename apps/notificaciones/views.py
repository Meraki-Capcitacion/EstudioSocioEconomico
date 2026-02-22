from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import Notificacion


class NotificacionListView(LoginRequiredMixin, ListView):
    model = Notificacion
    context_object_name = 'notificaciones'
    paginate_by = 25


class NotificacionDetailView(LoginRequiredMixin, DetailView):
    model = Notificacion
    context_object_name = 'notificacion'


class NotificacionCreateView(LoginRequiredMixin, CreateView):
    model = Notificacion
    fields = [
        'usuario', 'estudio', 'tipo',
        'titulo', 'mensaje', 'prioridad',
    ]
    success_url = reverse_lazy('notificaciones:notificacion_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class NotificacionUpdateView(LoginRequiredMixin, UpdateView):
    model = Notificacion
    fields = [
        'usuario', 'estudio', 'tipo',
        'titulo', 'mensaje', 'prioridad',
        'leida', 'fecha_lectura',
    ]
    success_url = reverse_lazy('notificaciones:notificacion_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class NotificacionDeleteView(LoginRequiredMixin, DeleteView):
    model = Notificacion
    context_object_name = 'notificacion'
    success_url = reverse_lazy('notificaciones:notificacion_list')
