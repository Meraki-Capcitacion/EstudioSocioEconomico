from django.urls import path

from . import views

app_name = 'usuarios'

urlpatterns = [
    path('mi-perfil/', views.MiPerfilView.as_view(), name='mi_perfil'),
    path('mi-perfil/editar/', views.MiPerfilEditarView.as_view(), name='mi_perfil_editar'),
    path('', views.UsuarioListView.as_view(), name='usuario_list'),
    path('crear/', views.CrearUsuarioView.as_view(), name='usuario_crear'),
    path('<int:user_pk>/rol/', views.UsuarioRolEditarView.as_view(), name='usuario_rol_editar'),
    path('<int:user_pk>/permisos/', views.PermisosUsuarioView.as_view(), name='usuario_permisos'),
]
