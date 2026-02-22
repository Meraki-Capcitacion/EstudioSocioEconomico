from django.urls import path

from . import views

app_name = 'estudios'

urlpatterns = [
    path('', views.EstudioListView.as_view(), name='estudio_list'),
    path('crear/', views.EstudioCreateView.as_view(), name='estudio_create'),
    path('<int:pk>/', views.EstudioDetailView.as_view(), name='estudio_detail'),
    path('<int:pk>/editar/', views.EstudioUpdateView.as_view(), name='estudio_update'),
    path('<int:pk>/eliminar/', views.EstudioDeleteView.as_view(), name='estudio_delete'),
    path('<int:pk>/cambiar-estado/', views.CambiarEstadoView.as_view(), name='cambiar_estado'),
]
