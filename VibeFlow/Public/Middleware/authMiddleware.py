"""
authMiddleware.py - Middleware de protección de rutas.
Equivalente a un middleware de Express.js que verifica sesión o JWT.
Verifica permisos por rol para las rutas API.
"""

from django.shortcuts import redirect
from django.http import JsonResponse
from VibeFlow.Public.Services import jwtService, routePermissionsService


# Mapeo de método HTTP a campo de permiso
METHOD_PERMISSION_MAP = {
    'GET': 'can_get',
    'POST': 'can_post',
    'PUT': 'can_put',
    'PATCH': 'can_put',
    'DELETE': 'can_delete',
}


class AuthMiddleware:
    """
    Rutas públicas (no requieren sesión):
      - /            → Login page
      - /api/auth/   → Login / Logout endpoints
      - /static/     → Archivos estáticos (CSS, JS, imágenes)
    
    Todo lo demás requiere sesión activa o token JWT válido.
    Las APIs verifican permisos por rol según el método HTTP.
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

        # ── Verificar JWT en header Authorization ──
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            payload = jwtService.verify_token(token)
            if payload:
                # Token válido: inyectar datos del usuario en request
                request.jwt_user = payload

                # Para APIs, verificar permisos por rol
                if path.startswith('/api/'):
                    perm_result = self._check_api_permission(request, payload)
                    if perm_result is not None:
                        return perm_result

                return self.get_response(request)

        # ── Verificar sesión (fallback) ──
        if request.session.get('is_authenticated'):
            return self.get_response(request)

        # ── No autorizado ──
        if path.startswith('/api/'):
            return JsonResponse({
                "status": False,
                "message": "No autorizado. Token inválido o expirado."
            }, status=401)

        # Si es una vista HTML, redirigir al login
        return redirect('/')

    def _check_api_permission(self, request, payload):
        """
        Verifica si los roles del usuario tienen permiso para el método HTTP
        en la ruta API solicitada. Retorna JsonResponse 403 si no tiene permiso,
        o None si todo está OK.
        """
        role_ids = payload.get('role_ids', [])
        method = request.method
        perm_field = METHOD_PERMISSION_MAP.get(method)

        if not perm_field or not role_ids:
            return None  # Métodos no mapeados pasan (OPTIONS, HEAD)

        # Obtener la ruta API base (ej: /api/routes/ → routes)
        # Las route_permissions controlan el acceso a las VISTAS,
        # y cada vista tiene una API asociada. Mapeamos:
        api_path = request.path

        # Verificar si alguno de los roles tiene el permiso requerido
        has_permission = routePermissionsService.check_api_permission(
            role_ids, api_path, perm_field
        )

        if not has_permission:
            return JsonResponse({
                "status": False,
                "message": f"Acceso denegado. Tu rol no tiene permiso de {method} en esta ruta."
            }, status=403)

        return None  # Permiso concedido
