from django.contrib import admin

from .models import SituacionEconomica


@admin.register(SituacionEconomica)
class SituacionEconomicaAdmin(admin.ModelAdmin):
    list_display = ('estudio', 'situacion_economica_percibida',
                    'salario_mensual', 'get_ingreso_total',
                    'get_egreso_total', 'get_capacidad_ahorro')
    list_filter = ('situacion_economica_percibida', 'tiene_automovil',
                   'tiene_creditos', 'automovil_con_adeudo')
    search_fields = ('estudio__persona__folio',
                     'estudio__persona__nombre',
                     'institucion_bancaria', 'afore')
    raw_id_fields = ('estudio',)
    list_per_page = 25

    fieldsets = (
        ('Estudio', {
            'fields': ('estudio', 'situacion_economica_percibida'),
        }),
        ('Ingresos', {
            'fields': ('salario_mensual', 'bonos_comisiones',
                       'ingresos_extra', 'apoyo_familiar',
                       'otros_ingresos', 'descripcion_otros_ingresos'),
        }),
        ('Egresos', {
            'fields': ('gasto_alimentacion', 'gasto_vivienda',
                       'gasto_servicios', 'gasto_transporte',
                       'gasto_educacion', 'gasto_salud',
                       'gasto_deudas', 'otros_gastos',
                       'descripcion_otros_gastos'),
        }),
        ('Patrimonio — Automóvil', {
            'fields': ('tiene_automovil', 'automovil_marca_modelo',
                       'automovil_anio', 'automovil_valor_comercial',
                       'automovil_con_adeudo'),
        }),
        ('Patrimonio — Inmueble', {
            'fields': ('patrimonio_inmobiliario', 'descripcion_patrimonio'),
        }),
        ('Cuenta bancaria y AFORE', {
            'fields': ('institucion_bancaria', 'afore'),
        }),
        ('Créditos y deudas', {
            'fields': ('tiene_creditos', 'credito_hipotecario',
                       'credito_automotriz', 'tarjetas_credito',
                       'tarjeta_credito_banco', 'tienda_departamental_nombre',
                       'tienda_departamental_adeudo', 'prestamos_personales',
                       'otros_creditos', 'descripcion_otros_creditos'),
        }),
    )

    @admin.display(description='Ingreso total')
    def get_ingreso_total(self, obj):
        return f'${obj.ingreso_total_mensual:,.2f}'

    @admin.display(description='Egreso total')
    def get_egreso_total(self, obj):
        return f'${obj.egreso_total_mensual:,.2f}'

    @admin.display(description='Capacidad de ahorro')
    def get_capacidad_ahorro(self, obj):
        return f'${obj.capacidad_ahorro:,.2f}'
