"""
urls.py - Archivo principal de rutas de VibeFlow.
Equivalente al app.use() de Express.js.
Cada módulo tiene su propio Router y aquí solo se hace el include con su prefijo.
"""

from django.urls import path, include, re_path

from VibeFlow.Public.Controllers.viewRoutesController import ViewRoutesController


urlpatterns = [
    # ─── API Routers (equivalente a app.use('/api/xxx', xxxRouter)) ─
    path('api/users/', include('VibeFlow.Public.Routes.usersRouter')),
    path('api/roles/', include('VibeFlow.Public.Routes.rolesRouter')),
    path('api/user-roles/', include('VibeFlow.Public.Routes.userRolesRouter')),
    path('api/routes/', include('VibeFlow.Public.Routes.viewRoutesRouter')),
    path('api/permissions/', include('VibeFlow.Public.Routes.routePermissionsRouter')),
    path('api/auth/', include('VibeFlow.Public.Routes.authRouter')),

    # ─── Vistas HTML dinámicas (se leen de la BD: app.view_routes) ────────
    # Catch-all: busca el url_path en la tabla view_routes y renderiza el template
    re_path(r'^(?P<url_path>.*)$', ViewRoutesController.dynamic_view, name='dynamic-view'),
]
