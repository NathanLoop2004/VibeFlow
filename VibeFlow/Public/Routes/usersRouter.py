"""
usersRouter.py - Rutas para el controlador de usuarios.
Equivalente a un express.Router() individual.
"""

from django.urls import path
from VibeFlow.Public.Controllers.usersController import UsersController

urlpatterns = [
    # GET /api/users/
    path('', UsersController.obtener_usuarios, name='api-users-list'),

    # POST /api/users/create/
    path('create/', UsersController.crear_usuario, name='api-users-create'),

    # GET /api/users/<uuid>/
    path('<uuid:user_id>/', UsersController.obtener_usuario_por_id, name='api-users-detail'),

    # PUT /api/users/<uuid>/update/
    path('<uuid:user_id>/update/', UsersController.actualizar_usuario, name='api-users-update'),

    # DELETE /api/users/<uuid>/delete/
    path('<uuid:user_id>/delete/', UsersController.eliminar_usuario, name='api-users-delete'),
]
