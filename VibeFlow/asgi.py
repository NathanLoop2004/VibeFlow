"""
ASGI config for VibeFlow project.

It exposes the ASGI callable as a module-level variable named ``application``.
Includes Django Channels WebSocket routing.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VibeFlow.settings')

# Inicializar Django primero (necesario para importar consumers)
django_asgi_app = get_asgi_application()

from VibeFlow.Public.Routes.websocket_routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http':      django_asgi_app,
    'websocket': URLRouter(websocket_urlpatterns),
})
