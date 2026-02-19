"""
routePermissionsModel.py - Modelo de permisos por ruta y usuario.
Define qué usuario puede acceder a qué ruta y con qué métodos HTTP.
"""

from django.db import models
from VibeFlow.Public.Models.usersModel import User
from VibeFlow.Public.Models.viewRoutesModel import ViewRoute


class RoutePermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='route_permissions')
    route = models.ForeignKey(ViewRoute, on_delete=models.CASCADE, related_name='permissions')
    can_get = models.BooleanField(default=False, help_text="Permiso para GET (ver la vista)")
    can_post = models.BooleanField(default=False, help_text="Permiso para POST (crear)")
    can_put = models.BooleanField(default=False, help_text="Permiso para PUT (actualizar)")
    can_delete = models.BooleanField(default=False, help_text="Permiso para DELETE (eliminar)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accounts'
        db_table = 'route_permissions'
        unique_together = ('user', 'route')
        ordering = ['route__url_path', 'user__username']

    def __str__(self):
        methods = []
        if self.can_get: methods.append('GET')
        if self.can_post: methods.append('POST')
        if self.can_put: methods.append('PUT')
        if self.can_delete: methods.append('DELETE')
        return f"{self.user.username} → {self.route.url_path} [{', '.join(methods)}]"
