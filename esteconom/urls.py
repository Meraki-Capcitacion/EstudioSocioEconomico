from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import include, path
from django.views.generic import TemplateView

from apps.personas.models import Persona
from apps.estudios.models import EstudioSocioeconomico


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_personas'] = Persona.objects.filter(activo=True).count()
        ctx['total_estudios'] = EstudioSocioeconomico.objects.count()
        ctx['estudios_en_proceso'] = EstudioSocioeconomico.objects.filter(estado='PRO').count()
        ctx['estudios_aprobados'] = EstudioSocioeconomico.objects.filter(estado='APR').count()
        return ctx


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    path('configuracion/', include('apps.configuracion.urls')),
    path('personas/', include('apps.personas.urls')),
    path('estudios/', include('apps.estudios.urls')),
    path('domicilios/', include('apps.domicilios.urls')),
    path('economia/', include('apps.economia.urls')),
    path('educacion/', include('apps.educacion.urls')),
    path('laboral/', include('apps.laboral.urls')),
    path('familia/', include('apps.familia.urls')),
    path('referencias/', include('apps.referencias.urls')),
    path('visitas/', include('apps.visitas.urls')),
    path('evaluacion/', include('apps.evaluacion.urls')),
    path('documentos/', include('apps.documentos.urls')),
    path('notificaciones/', include('apps.notificaciones.urls')),
    path('candidato/', include('apps.estudios.urls_candidato')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
