"""
routePermissionsRouter.py - Rutas para el controlador de permisos de rutas.
Equivalente a un express.Router() individual.
"""

from django.urls import path
from VibeFlow.Public.Controllers.routePermissionsController import RoutePermissionsController

urlpatterns = [
    # GET /api/permissions/
    path('', RoutePermissionsController.obtener_permisos, name='api-permissions-list'),

    # POST /api/permissions/create/
    path('create/', RoutePermissionsController.crear_permiso, name='api-permissions-create'),

    # PUT /api/permissions/<id>/update/
    path('<int:perm_id>/update/', RoutePermissionsController.actualizar_permiso, name='api-permissions-update'),

    # DELETE /api/permissions/<id>/delete/
    path('<int:perm_id>/delete/', RoutePermissionsController.eliminar_permiso, name='api-permissions-delete'),

    # GET /api/permissions/route/<id>/
    path('route/<int:route_id>/', RoutePermissionsController.obtener_permisos_por_ruta, name='api-permissions-by-route'),

    # GET /api/permissions/user/<uuid>/
    path('user/<uuid:user_id>/', RoutePermissionsController.obtener_permisos_por_usuario, name='api-permissions-by-user'),
]
