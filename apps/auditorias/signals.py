from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.documentos.models import Documento
from apps.estudios.models import EstudioSocioeconomico
from apps.evaluacion.models import EvaluacionRiesgo
from apps.laboral.models import HistorialLaboral
from apps.personas.models import Persona
from apps.referencias.models import Referencia


def _registrar(accion, instance, descripcion, datos_antes=None, datos_despues=None):
    """Crea un RegistroAuditoria usando el request del thread-local si está disponible."""
    from .middleware import get_current_request
    from .models import RegistroAuditoria

    request = get_current_request()
    usuario = None
    ip = None
    if request is not None:
        if hasattr(request, 'user') and request.user.is_authenticated:
            usuario = request.user
        ip = request.META.get('REMOTE_ADDR')

    RegistroAuditoria.objects.create(
        usuario=usuario,
        accion=accion,
        modelo=instance.__class__.__name__,
        objeto_id=instance.pk,
        descripcion=descripcion,
        datos_antes=datos_antes,
        datos_despues=datos_despues,
        ip_address=ip,
    )


# ---------------------------------------------------------------------------
# Persona
# ---------------------------------------------------------------------------

@receiver(pre_save, sender=Persona)
def persona_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._pre_save_nombre = Persona.objects.values('nombre', 'apellido_paterno').get(pk=instance.pk)
        except Persona.DoesNotExist:
            instance._pre_save_nombre = None
    else:
        instance._pre_save_nombre = None


@receiver(post_save, sender=Persona)
def persona_post_save(sender, instance, created, **kwargs):
    if created:
        _registrar('CRE', instance,
                   f'Creó persona: {instance.nombre_completo} (folio: {instance.folio})')
    else:
        antes = getattr(instance, '_pre_save_nombre', None)
        _registrar('MOD', instance,
                   f'Modificó persona: {instance.nombre_completo} (folio: {instance.folio})',
                   datos_antes=antes,
                   datos_despues={'nombre': instance.nombre, 'apellido_paterno': instance.apellido_paterno})


# ---------------------------------------------------------------------------
# EstudioSocioeconomico
# ---------------------------------------------------------------------------

@receiver(pre_save, sender=EstudioSocioeconomico)
def estudio_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._pre_save_estado = EstudioSocioeconomico.objects.values('estado').get(pk=instance.pk)['estado']
        except EstudioSocioeconomico.DoesNotExist:
            instance._pre_save_estado = None
    else:
        instance._pre_save_estado = None


@receiver(post_save, sender=EstudioSocioeconomico)
def estudio_post_save(sender, instance, created, **kwargs):
    persona_str = instance.persona.nombre_completo if instance.persona_id else f'#{instance.pk}'
    if created:
        _registrar('CRE', instance,
                   f'Creó estudio para: {persona_str}',
                   datos_despues={'estado': instance.estado})
    else:
        estado_antes = getattr(instance, '_pre_save_estado', None)
        if estado_antes and estado_antes != instance.estado:
            _registrar('CAM', instance,
                       f'Cambió estado de estudio ({persona_str}): {estado_antes} → {instance.estado}',
                       datos_antes={'estado': estado_antes},
                       datos_despues={'estado': instance.estado})
        else:
            _registrar('MOD', instance,
                       f'Modificó estudio de: {persona_str}')


# ---------------------------------------------------------------------------
# EvaluacionRiesgo
# ---------------------------------------------------------------------------

@receiver(post_save, sender=EvaluacionRiesgo)
def evaluacion_post_save(sender, instance, created, **kwargs):
    persona_str = instance.estudio.persona.nombre_completo if instance.estudio_id else f'#{instance.pk}'
    accion = 'CRE' if created else 'MOD'
    verbo = 'Creó' if created else 'Modificó'
    _registrar(accion, instance,
               f'{verbo} evaluación de riesgo para: {persona_str}',
               datos_despues={'score_final': str(instance.score_final), 'nivel_riesgo': instance.nivel_riesgo})


# ---------------------------------------------------------------------------
# Documento — registrar cuando se verifica
# ---------------------------------------------------------------------------

@receiver(pre_save, sender=Documento)
def documento_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._pre_verificado = Documento.objects.values('verificado').get(pk=instance.pk)['verificado']
        except Documento.DoesNotExist:
            instance._pre_verificado = False
    else:
        instance._pre_verificado = False


@receiver(post_save, sender=Documento)
def documento_post_save(sender, instance, created, **kwargs):
    if not created and not getattr(instance, '_pre_verificado', False) and instance.verificado:
        _registrar('VER', instance,
                   f'Verificó documento: {instance.get_tipo_display()} — {instance.nombre_archivo}')


# ---------------------------------------------------------------------------
# HistorialLaboral — registrar cuando se verifica
# ---------------------------------------------------------------------------

@receiver(pre_save, sender=HistorialLaboral)
def laboral_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._pre_verificada = HistorialLaboral.objects.values('verificada').get(pk=instance.pk)['verificada']
        except HistorialLaboral.DoesNotExist:
            instance._pre_verificada = False
    else:
        instance._pre_verificada = False


@receiver(post_save, sender=HistorialLaboral)
def laboral_post_save(sender, instance, created, **kwargs):
    if not created and not getattr(instance, '_pre_verificada', False) and instance.verificada:
        persona_str = instance.persona.nombre_completo if instance.persona_id else f'#{instance.pk}'
        _registrar('VER', instance,
                   f'Verificó historial laboral: {instance.empresa} — {instance.puesto} ({persona_str})')


# ---------------------------------------------------------------------------
# Referencia — registrar cuando se verifica
# ---------------------------------------------------------------------------

@receiver(pre_save, sender=Referencia)
def referencia_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._pre_verificada = Referencia.objects.values('verificada').get(pk=instance.pk)['verificada']
        except Referencia.DoesNotExist:
            instance._pre_verificada = False
    else:
        instance._pre_verificada = False


@receiver(post_save, sender=Referencia)
def referencia_post_save(sender, instance, created, **kwargs):
    if not created and not getattr(instance, '_pre_verificada', False) and instance.verificada:
        persona_str = instance.persona.nombre_completo if instance.persona_id else f'#{instance.pk}'
        _registrar('VER', instance,
                   f'Verificó referencia: {instance.nombre} ({persona_str})')


# ---------------------------------------------------------------------------
# Post-delete genérico para modelos clave
# ---------------------------------------------------------------------------

def _registrar_eliminacion(sender, instance, **kwargs):
    nombre_modelo = sender.__name__
    _registrar('ELI', instance, f'Eliminó {nombre_modelo} #{instance.pk}')


for _modelo in (Persona, EstudioSocioeconomico, EvaluacionRiesgo, Documento, HistorialLaboral, Referencia):
    post_delete.connect(_registrar_eliminacion, sender=_modelo)
