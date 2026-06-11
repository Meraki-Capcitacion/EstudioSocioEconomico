from django.apps import AppConfig


class AuditoriaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auditorias'
    verbose_name = 'Auditorías'

    def ready(self):
        import apps.auditorias.signals  # noqa: F401
