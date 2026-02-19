"""
urls.py - Archivo principal de rutas de VibeFlow.
Equivalente al app.use() de Express.js.
Cada módulo tiene su propio Router y aquí solo se hace el include con su prefijo.
"""

from django.urls import path, include, re_path
from django.views.generic import TemplateView

from VibeFlow.Public.Controllers.viewRoutesController import ViewRoutesController


urlpatterns = [
    # ─── Login (página de inicio) ─
    path('', TemplateView.as_view(template_name='Login/login.html'), name='login'),

    # ─── Registro ─
    path('register/', TemplateView.as_view(template_name='Register/register.html'), name='register'),

    # ─── Panel (requiere estar autenticado) ─
    path('panel/', TemplateView.as_view(template_name='Panel/panel.html'), name='panel'),

    # ─── API Routers (equivalente a app.use('/api/xxx', xxxRouter)) ─
    path('api/users/', include('VibeFlow.Public.Routes.usersRouter')),
    path('api/roles/', include('VibeFlow.Public.Routes.rolesRouter')),
    path('api/user-roles/', include('VibeFlow.Public.Routes.userRolesRouter')),
    path('api/routes/', include('VibeFlow.Public.Routes.viewRoutesRouter')),
    path('api/permissions/', include('VibeFlow.Public.Routes.routePermissionsRouter')),
    path('api/auth/', include('VibeFlow.Public.Routes.authRouter')),

    # ─── Vistas HTML dinámicas (se leen de la BD) ────────
    # Este catch-all va AL FINAL para no interceptar las rutas de API
    re_path(r'^(?P<url_path>.+)$', ViewRoutesController.dynamic_view, name='dynamic-view'),
]
