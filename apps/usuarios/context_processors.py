from .models import PerfilUsuario, MODULOS_DISPONIBLES

_TODOS_LOS_MODULOS = {m[0] for m in MODULOS_DISPONIBLES}


def perfil_usuario(request):
    """
    Inyecta en todos los templates:
      - perfil_usuario
      - es_analista, es_inspector, es_auditor
      - modulos_permitidos  (conjunto de claves de módulo accesibles)
    """
    if not request.user.is_authenticated:
        return {
            'perfil_usuario': None,
            'es_analista': False,
            'es_inspector': False,
            'es_auditor': False,
            'modulos_permitidos': set(),
        }

    if request.user.is_superuser:
        return {
            'perfil_usuario': None,
            'es_analista': True,
            'es_inspector': False,
            'es_auditor': False,
            'modulos_permitidos': _TODOS_LOS_MODULOS,
        }

    try:
        perfil = request.user.perfil
    except PerfilUsuario.DoesNotExist:
        perfil = None

    return {
        'perfil_usuario': perfil,
        'es_analista': perfil.es_analista if perfil else False,
        'es_inspector': perfil.es_inspector if perfil else False,
        'es_auditor': perfil.es_auditor if perfil else False,
        'modulos_permitidos': perfil.get_modulos_permitidos() if perfil else set(),
    }
