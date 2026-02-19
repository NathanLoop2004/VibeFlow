"""
viewRoutesRouter.py - Rutas para el controlador de rutas de vistas (CRUD).
Equivalente a un express.Router() individual.
Nota: dynamic_view se registra directamente en urls.py (catch-all).
"""

from django.urls import path
from VibeFlow.Public.Controllers.viewRoutesController import ViewRoutesController

urlpatterns = [
    # GET /api/routes/
    path('', ViewRoutesController.obtener_rutas, name='api-routes-list'),

    # POST /api/routes/create/
    path('create/', ViewRoutesController.crear_ruta, name='api-routes-create'),

    # GET /api/routes/<id>/
    path('<int:route_id>/', ViewRoutesController.obtener_ruta_por_id, name='api-routes-detail'),

    # PUT /api/routes/<id>/update/
    path('<int:route_id>/update/', ViewRoutesController.actualizar_ruta, name='api-routes-update'),

    # DELETE /api/routes/<id>/delete/
    path('<int:route_id>/delete/', ViewRoutesController.eliminar_ruta, name='api-routes-delete'),

    # PATCH /api/routes/<id>/toggle/
    path('<int:route_id>/toggle/', ViewRoutesController.toggle_ruta, name='api-routes-toggle'),
]
