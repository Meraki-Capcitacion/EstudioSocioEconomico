from django.urls import path

from . import views

app_name = 'documentos'

urlpatterns = [
    path('', views.DocumentoListView.as_view(), name='documento_list'),
    path('crear/', views.DocumentoCreateView.as_view(), name='documento_create'),
    path('estudios-por-persona/', views.EstudiosPorPersonaView.as_view(), name='estudios_por_persona'),
    path('<int:pk>/', views.DocumentoDetailView.as_view(), name='documento_detail'),
    path('<int:pk>/editar/', views.DocumentoUpdateView.as_view(), name='documento_update'),
    path('<int:pk>/eliminar/', views.DocumentoDeleteView.as_view(), name='documento_delete'),
]
