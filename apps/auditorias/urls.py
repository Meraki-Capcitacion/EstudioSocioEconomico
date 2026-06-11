from django.urls import path

from . import views

app_name = 'auditorias'

urlpatterns = [
    path('', views.AuditoriaListView.as_view(), name='auditoria_list'),
]
