import django.db.models.deletion
from django.db import migrations, models


def crear_permisos_default(apps, schema_editor):
    """Crea permisos explícitos para todos los perfiles existentes según su rol."""
    PerfilUsuario = apps.get_model('usuarios', 'PerfilUsuario')
    PermisoModulo = apps.get_model('usuarios', 'PermisoModulo')

    MODULOS_POR_ROL = {
        'ANA': [
            'personas', 'estudios', 'domicilios', 'economia', 'educacion',
            'laboral', 'familia', 'referencias', 'visitas', 'evaluacion',
            'documentos', 'notificaciones', 'reportes', 'configuracion',
        ],
        'INS': ['visitas', 'referencias', 'laboral', 'documentos', 'notificaciones'],
        'AUD': [
            'personas', 'estudios', 'domicilios', 'economia', 'educacion',
            'laboral', 'familia', 'referencias', 'visitas', 'evaluacion',
            'documentos', 'notificaciones', 'reportes', 'configuracion',
        ],
    }

    for perfil in PerfilUsuario.objects.all():
        for modulo in MODULOS_POR_ROL.get(perfil.rol, []):
            PermisoModulo.objects.get_or_create(perfil=perfil, modulo=modulo)


def revertir_permisos_default(apps, schema_editor):
    PermisoModulo = apps.get_model('usuarios', 'PermisoModulo')
    PermisoModulo.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfilusuario',
            name='rol',
            field=models.CharField(
                choices=[('ANA', 'Analista'), ('INS', 'Inspector'), ('AUD', 'Auditor')],
                default='ANA',
                help_text='Determina las funciones a las que tiene acceso el usuario.',
                max_length=3,
                verbose_name='Rol',
            ),
        ),
        migrations.CreateModel(
            name='PermisoModulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modulo', models.CharField(
                    choices=[
                        ('personas', 'Personas'),
                        ('estudios', 'Estudios Socioeconómicos'),
                        ('domicilios', 'Domicilios'),
                        ('educacion', 'Educación e Idiomas'),
                        ('laboral', 'Historial Laboral'),
                        ('familia', 'Grupo Familiar'),
                        ('referencias', 'Referencias'),
                        ('economia', 'Situación Económica'),
                        ('visitas', 'Visitas Domiciliarias'),
                        ('evaluacion', 'Evaluación de Riesgo'),
                        ('documentos', 'Documentos'),
                        ('notificaciones', 'Notificaciones'),
                        ('reportes', 'Reportes PDF'),
                        ('configuracion', 'Configuración'),
                    ],
                    max_length=20,
                    verbose_name='Módulo',
                )),
                ('perfil', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='permisos_modulos',
                    to='usuarios.perfilusuario',
                    verbose_name='Perfil',
                )),
            ],
            options={
                'verbose_name': 'Permiso de módulo',
                'verbose_name_plural': 'Permisos de módulos',
                'ordering': ['modulo'],
                'unique_together': {('perfil', 'modulo')},
            },
        ),
        migrations.RunPython(crear_permisos_default, revertir_permisos_default),
    ]
