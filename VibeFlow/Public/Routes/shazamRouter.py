"""
shazamRouter.py - Rutas para el controlador Shazam MVP.
"""

from django.urls import path
from VibeFlow.Public.Controllers.shazamController import ShazamController

urlpatterns = [
    # GET /api/shazam/ — listar canciones
    path('', ShazamController.obtener_canciones, name='api-shazam-list'),

    # POST /api/shazam/upload/ — subir canción + generar fingerprints
    path('upload/', ShazamController.subir_cancion, name='api-shazam-upload'),

    # POST /api/shazam/search/ — buscar canción por audio
    path('search/', ShazamController.buscar_cancion, name='api-shazam-search'),

    # GET /api/shazam/<id>/ — detalle canción
    path('<int:song_id>/', ShazamController.obtener_cancion, name='api-shazam-detail'),

    # GET /api/shazam/<id>/audio/ — descargar audio
    path('<int:song_id>/audio/', ShazamController.audio_cancion, name='api-shazam-audio'),

    # PUT /api/shazam/<id>/update/ — actualizar canción
    path('<int:song_id>/update/', ShazamController.actualizar_cancion, name='api-shazam-update'),

    # DELETE /api/shazam/<id>/delete/ — eliminar canción
    path('<int:song_id>/delete/', ShazamController.eliminar_cancion, name='api-shazam-delete'),

    # POST /api/shazam/<id>/regenerate/ — regenerar fingerprints de 1 canción
    path('<int:song_id>/regenerate/', ShazamController.regenerar_cancion, name='api-shazam-regenerate'),

    # POST /api/shazam/regenerate-all/ — regenerar fingerprints de TODAS
    path('regenerate-all/', ShazamController.regenerar_todas, name='api-shazam-regenerate-all'),
]
