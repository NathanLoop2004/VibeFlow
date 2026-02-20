"""
recordingsRouter.py - Rutas para el controlador de grabaciones.
"""

from django.urls import path
from VibeFlow.Public.Controllers.recordingsController import RecordingsController

urlpatterns = [
    # GET /api/recordings/
    path('', RecordingsController.obtener_grabaciones, name='api-recordings-list'),

    # GET /api/recordings/mine/
    path('mine/', RecordingsController.obtener_mis_grabaciones, name='api-recordings-mine'),

    # POST /api/recordings/create/
    path('create/', RecordingsController.crear_grabacion, name='api-recordings-create'),

    # GET /api/recordings/<id>/
    path('<int:recording_id>/', RecordingsController.obtener_grabacion_por_id, name='api-recordings-detail'),

    # GET /api/recordings/<id>/audio/
    path('<int:recording_id>/audio/', RecordingsController.descargar_audio, name='api-recordings-audio'),

    # PUT /api/recordings/<id>/update/
    path('<int:recording_id>/update/', RecordingsController.actualizar_grabacion, name='api-recordings-update'),

    # DELETE /api/recordings/<id>/delete/
    path('<int:recording_id>/delete/', RecordingsController.eliminar_grabacion, name='api-recordings-delete'),
]
