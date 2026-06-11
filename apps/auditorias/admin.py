from django.contrib import admin

from .models import RegistroAuditoria


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'usuario', 'accion', 'modelo', 'objeto_id', 'descripcion', 'ip_address')
    list_filter = ('accion', 'modelo', 'created_at')
    search_fields = ('descripcion', 'usuario__username', 'modelo')
    readonly_fields = ('usuario', 'accion', 'modelo', 'objeto_id', 'descripcion',
                       'datos_antes', 'datos_despues', 'ip_address', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
