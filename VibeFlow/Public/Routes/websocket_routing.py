"""
websocket_routing.py - Rutas WebSocket de VibeFlow.
Equivalente al routing de Django Channels.
"""

from django.urls import path
from VibeFlow.Public.Consumers.shazamConsumer import ShazamStreamConsumer

websocket_urlpatterns = [
    # ws://localhost:8000/ws/shazam/
    path('ws/shazam/', ShazamStreamConsumer.as_asgi()),
]
