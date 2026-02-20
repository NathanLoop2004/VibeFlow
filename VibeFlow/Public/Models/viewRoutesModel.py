"""
viewRoutesModel.py - Modelo para almacenar las rutas de vistas HTML en la BD.
Cada registro representa un path URL que apunta a un template HTML.
Soporta jerarquía: módulo → familia → subfamilia.
"""

from django.db import models


class ViewRoute(models.Model):
    url_path = models.CharField(max_length=255, unique=True, help_text="Ruta URL, ej: views/users/")
    template_name = models.CharField(max_length=255, help_text="Ruta del template, ej: Users/users.html")
    name = models.CharField(max_length=100, unique=True, help_text="Nombre único de la ruta, ej: view-users")
    is_active = models.BooleanField(default=True, help_text="Si la ruta está habilitada o no")

    # Jerarquía del menú (todos nullable para rutas de sistema como login/register)
    module = models.ForeignKey(
        'accounts.Module', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='routes',
        help_text="Módulo al que pertenece (nivel 1)"
    )
    family = models.ForeignKey(
        'accounts.Family', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='routes',
        help_text="Familia a la que pertenece (nivel 2)"
    )
    subfamily = models.ForeignKey(
        'accounts.Subfamily', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='routes',
        help_text="Subfamilia a la que pertenece (nivel 3)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accounts'
        db_table = 'view_routes'
        ordering = ['url_path']

    def __str__(self):
        return f"{self.url_path} → {self.template_name}"
