from django.urls import path

from . import views

app_name = 'personas'

urlpatterns = [
    path('', views.PersonaListView.as_view(), name='persona_list'),
    path('crear/', views.PersonaCreateView.as_view(), name='persona_create'),
    path('<int:pk>/', views.PersonaDetailView.as_view(), name='persona_detail'),
    path('<int:pk>/editar/', views.PersonaUpdateView.as_view(), name='persona_update'),
    path('<int:pk>/eliminar/', views.PersonaDeleteView.as_view(), name='persona_delete'),
    # Salud
    path('salud/crear/', views.SaludPersonaCreateView.as_view(), name='saludpersona_create'),
    path('salud/<int:pk>/editar/', views.SaludPersonaUpdateView.as_view(), name='saludpersona_update'),
]
