"""
modulesRouter.py - Rutas para el controlador de módulos (CRUD).
"""

from django.urls import path
from VibeFlow.Public.Controllers.modulesController import ModulesController

urlpatterns = [
    # GET /api/modules/
    path('', ModulesController.obtener_modulos, name='api-modules-list'),

    # POST /api/modules/create/
    path('create/', ModulesController.crear_modulo, name='api-modules-create'),

    # PUT /api/modules/<id>/update/
    path('<int:module_id>/update/', ModulesController.actualizar_modulo, name='api-modules-update'),

    # DELETE /api/modules/<id>/delete/
    path('<int:module_id>/delete/', ModulesController.eliminar_modulo, name='api-modules-delete'),
]
