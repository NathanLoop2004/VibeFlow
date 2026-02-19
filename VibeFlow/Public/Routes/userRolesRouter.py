"""
userRolesRouter.py - Rutas para el controlador de asignación de roles.
Equivalente a un express.Router() individual.
"""

from django.urls import path
from VibeFlow.Public.Controllers.userRolesController import UserRolesController

urlpatterns = [
    # GET /api/user-roles/
    path('', UserRolesController.obtener_asignaciones, name='api-user-roles-list'),

    # POST /api/user-roles/assign/
    path('assign/', UserRolesController.asignar_rol, name='api-user-roles-assign'),

    # GET /api/user-roles/user/<uuid>/
    path('user/<uuid:user_id>/', UserRolesController.obtener_roles_por_usuario, name='api-user-roles-by-user'),

    # GET /api/user-roles/role/<id>/
    path('role/<int:role_id>/', UserRolesController.obtener_usuarios_por_rol, name='api-user-roles-by-role'),

    # DELETE /api/user-roles/<uuid>/<id>/delete/
    path('<uuid:user_id>/<int:role_id>/delete/', UserRolesController.eliminar_asignacion, name='api-user-roles-delete'),
]
