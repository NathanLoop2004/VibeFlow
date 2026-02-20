"""
familiesRouter.py - Rutas para el controlador de familias (CRUD).
"""

from django.urls import path
from VibeFlow.Public.Controllers.familiesController import FamiliesController

urlpatterns = [
    # GET /api/families/
    path('', FamiliesController.obtener_familias, name='api-families-list'),

    # GET /api/families/module/<id>/
    path('module/<int:module_id>/', FamiliesController.obtener_por_modulo, name='api-families-by-module'),

    # POST /api/families/create/
    path('create/', FamiliesController.crear_familia, name='api-families-create'),

    # PUT /api/families/<id>/update/
    path('<int:family_id>/update/', FamiliesController.actualizar_familia, name='api-families-update'),

    # DELETE /api/families/<id>/delete/
    path('<int:family_id>/delete/', FamiliesController.eliminar_familia, name='api-families-delete'),
]
