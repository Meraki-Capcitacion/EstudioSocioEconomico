from django.core.exceptions import PermissionDenied

# Mapeo de prefijo de URL → clave de módulo protegido
MODULO_POR_PREFIJO = {
    '/personas/': 'personas',
    '/estudios/': 'estudios',
    '/domicilios/': 'domicilios',
    '/economia/': 'economia',
    '/educacion/': 'educacion',
    '/laboral/': 'laboral',
    '/familia/': 'familia',
    '/referencias/': 'referencias',
    '/visitas/': 'visitas',
    '/evaluacion/': 'evaluacion',
    '/documentos/': 'documentos',
    '/notificaciones/': 'notificaciones',
    '/reportes/': 'reportes',
    '/configuracion/': 'configuracion',
}


class ModuloPermisosMiddleware:
    """
    Verifica que el usuario autenticado tenga permiso para acceder
    al módulo correspondiente a la URL solicitada.

    Rutas exentas: /admin/, /accounts/, /candidato/, /usuarios/, /
    Superusuarios siempre tienen acceso completo.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        # Solo actuar si el usuario está autenticado y no es superusuario
        if not request.user.is_authenticated or request.user.is_superuser:
            return self.get_response(request)

        # Detectar a qué módulo pertenece esta ruta
        modulo = None
        for prefijo, mod in MODULO_POR_PREFIJO.items():
            if path.startswith(prefijo):
                modulo = mod
                break

        # Ruta no protegida por módulo → continuar sin verificar
        if modulo is None:
            return self.get_response(request)

        # Obtener perfil y verificar permiso
        try:
            perfil = request.user.perfil
        except Exception:
            raise PermissionDenied

        if not perfil.activo:
            raise PermissionDenied

        if not perfil.tiene_permiso_modulo(modulo):
            raise PermissionDenied

        return self.get_response(request)
