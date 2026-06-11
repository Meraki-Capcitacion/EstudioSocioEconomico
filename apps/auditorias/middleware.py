import threading

_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, 'request', None)


class AuditoriaMiddleware:
    """Almacena el request actual en thread-local para que los signals lo puedan leer."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        try:
            response = self.get_response(request)
        finally:
            # Limpiar para evitar filtraciones entre requests en el mismo thread
            _thread_locals.request = None
        return response
