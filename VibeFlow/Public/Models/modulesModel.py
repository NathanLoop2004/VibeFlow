"""
modulesModel.py - Modelo para módulos (nivel superior del menú).
"""

from django.db import models


class Module(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, help_text="Nombre del módulo")
    icon = models.CharField(max_length=50, default='📁', help_text="Icono emoji o clase CSS")
    display_order = models.IntegerField(default=0, help_text="Orden de presentación")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accounts'
        db_table = 'modules'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name
