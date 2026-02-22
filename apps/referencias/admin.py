from django.contrib import admin
from django.utils import timezone

from .models import Referencia


@admin.register(Referencia)
class ReferenciaAdmin(admin.ModelAdmin):
    list_display = ('persona', 'nombre', 'tipo',
                    'parentesco_o_relacion', 'tiempo_conocer_anios',
                    'verificada', 'fecha_verificacion')
    list_filter = ('tipo', 'verificada')
    search_fields = ('persona__folio', 'persona__nombre',
                     'nombre', 'parentesco_o_relacion')
    raw_id_fields = ('persona',)
    readonly_fields = ('fecha_verificacion', 'created_at',
                       'updated_at', 'created_by', 'updated_by')
    list_per_page = 25

    fieldsets = (
        ('Persona evaluada', {
            'fields': ('persona',),
        }),
        ('Datos de la referencia', {
            'fields': ('tipo', 'nombre', 'telefono', 'email',
                       'parentesco_o_relacion', 'tiempo_conocer_anios',
                       'domicilio'),
        }),
        ('Información capturada al contactar', {
            'fields': ('actividad_tiempo_libre', 'lugares_laborado',
                       'conducta', 'cualidades'),
            'classes': ('collapse',),
        }),
        ('Verificación', {
            'fields': ('verificada', 'fecha_verificacion',
                       'comentarios_verificacion'),
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at',
                       'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    actions = ['marcar_verificada']

    @admin.action(description='Marcar como verificada')
    def marcar_verificada(self, request, queryset):
        updated = queryset.filter(verificada=False).update(
            verificada=True, fecha_verificacion=timezone.now()
        )
        self.message_user(request, f'{updated} referencia(s) marcada(s) como verificada(s).')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
