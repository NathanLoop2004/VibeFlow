"""
authRouter.py - Rutas para autenticación.
Equivalente a un express.Router() individual.
"""

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from VibeFlow.Public.Controllers.authController import AuthController

urlpatterns = [
    # POST /api/auth/login/
    path('login/', csrf_exempt(AuthController.login), name='api-auth-login'),
    # POST /api/auth/logout/
    path('logout/', csrf_exempt(AuthController.logout), name='api-auth-logout'),
    # POST /api/auth/register/
    path('register/', csrf_exempt(AuthController.register), name='api-auth-register'),
    # POST /api/auth/google/
    path('google/', csrf_exempt(AuthController.google_login), name='api-auth-google'),
    # GET /api/auth/google/callback/  (OAuth2 redirect callback)
    path('google/callback/', AuthController.google_callback, name='api-auth-google-callback'),
    # GET /api/auth/my-routes/
    path('my-routes/', AuthController.my_routes, name='api-auth-my-routes'),
]
