"""
rolesRouter.py - Rutas para el controlador de roles.
Equivalente a un express.Router() individual.
"""

from django.urls import path
from VibeFlow.Public.Controllers.rolesController import RolesController

urlpatterns = [
    # GET /api/roles/
    path('', RolesController.obtener_roles, name='api-roles-list'),

    # POST /api/roles/create/
    path('create/', RolesController.crear_rol, name='api-roles-create'),

    # GET /api/roles/<id>/
    path('<int:role_id>/', RolesController.obtener_rol_por_id, name='api-roles-detail'),

    # PUT /api/roles/<id>/update/
    path('<int:role_id>/update/', RolesController.actualizar_rol, name='api-roles-update'),

    # DELETE /api/roles/<id>/delete/
    path('<int:role_id>/delete/', RolesController.eliminar_rol, name='api-roles-delete'),
]
