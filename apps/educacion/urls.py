from django.urls import path

from . import views

app_name = 'educacion'

urlpatterns = [
    # NivelEducativo
    path('niveles/', views.NivelEducativoListView.as_view(), name='niveleducativo_list'),
    path('niveles/crear/', views.NivelEducativoCreateView.as_view(), name='niveleducativo_create'),
    path('niveles/<int:pk>/', views.NivelEducativoDetailView.as_view(), name='niveleducativo_detail'),
    path('niveles/<int:pk>/editar/', views.NivelEducativoUpdateView.as_view(), name='niveleducativo_update'),
    path('niveles/<int:pk>/eliminar/', views.NivelEducativoDeleteView.as_view(), name='niveleducativo_delete'),

    # Educacion
    path('', views.EducacionListView.as_view(), name='educacion_list'),
    path('crear/', views.EducacionCreateView.as_view(), name='educacion_create'),
    path('<int:pk>/', views.EducacionDetailView.as_view(), name='educacion_detail'),
    path('<int:pk>/editar/', views.EducacionUpdateView.as_view(), name='educacion_update'),
    path('<int:pk>/eliminar/', views.EducacionDeleteView.as_view(), name='educacion_delete'),

    # Idioma
    path('idiomas/', views.IdiomaListView.as_view(), name='idioma_list'),
    path('idiomas/crear/', views.IdiomaCreateView.as_view(), name='idioma_create'),
    path('idiomas/<int:pk>/', views.IdiomaDetailView.as_view(), name='idioma_detail'),
    path('idiomas/<int:pk>/editar/', views.IdiomaUpdateView.as_view(), name='idioma_update'),
    path('idiomas/<int:pk>/eliminar/', views.IdiomaDeleteView.as_view(), name='idioma_delete'),
]
