"""
subfamiliesRouter.py - Rutas para el controlador de subfamilias (CRUD).
"""

from django.urls import path
from VibeFlow.Public.Controllers.subfamiliesController import SubfamiliesController

urlpatterns = [
    # GET /api/subfamilies/
    path('', SubfamiliesController.obtener_subfamilias, name='api-subfamilies-list'),

    # GET /api/subfamilies/family/<id>/
    path('family/<int:family_id>/', SubfamiliesController.obtener_por_familia, name='api-subfamilies-by-family'),

    # POST /api/subfamilies/create/
    path('create/', SubfamiliesController.crear_subfamilia, name='api-subfamilies-create'),

    # PUT /api/subfamilies/<id>/update/
    path('<int:sf_id>/update/', SubfamiliesController.actualizar_subfamilia, name='api-subfamilies-update'),

    # DELETE /api/subfamilies/<id>/delete/
    path('<int:sf_id>/delete/', SubfamiliesController.eliminar_subfamilia, name='api-subfamilies-delete'),
]
