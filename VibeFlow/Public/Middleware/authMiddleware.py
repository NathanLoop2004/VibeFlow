"""
authMiddleware.py - Middleware de protección de rutas.
Equivalente a un middleware de Express.js que verifica sesión.

Si el usuario NO tiene sesión activa y NO está en una ruta pública,
se redirige automáticamente al login ( / ).
"""

from django.shortcuts import redirect


class AuthMiddleware:
    """
    Rutas públicas (no requieren sesión):
      - /            → Login page
      - /api/auth/   → Login / Logout endpoints
      - /static/     → Archivos estáticos (CSS, JS, imágenes)
    
    Todo lo demás requiere sesión activa.
    """

    PUBLIC_PREFIXES = (
        '/api/auth/',
        '/static/',
    )

    PUBLIC_PATHS = (
        '/',
        '/register/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # ── Rutas públicas: pasar sin verificar ──
        if path in self.PUBLIC_PATHS or any(path.startswith(p) for p in self.PUBLIC_PREFIXES):
            return self.get_response(request)

        # ── Verificar sesión ──
        if not request.session.get('is_authenticated'):
            # Si es una petición API, devolver 401 en lugar de redirect
            if path.startswith('/api/'):
                from django.http import JsonResponse
                return JsonResponse({
                    "status": False,
                    "message": "No autorizado. Inicia sesión primero."
                }, status=401)

            # Si es una vista HTML, redirigir al login
            return redirect('/')

        return self.get_response(request)
