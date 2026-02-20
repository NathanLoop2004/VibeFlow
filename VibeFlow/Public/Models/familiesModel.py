"""
familiesModel.py - Modelo para familias (segundo nivel del menú).
Cada familia pertenece a un módulo.
"""

from django.db import models


class Family(models.Model):
    id = models.AutoField(primary_key=True)
    module = models.ForeignKey(
        'accounts.Module',
        on_delete=models.CASCADE,
        related_name='families',
        help_text="Módulo al que pertenece"
    )
    name = models.CharField(max_length=100, help_text="Nombre de la familia")
    icon = models.CharField(max_length=50, default='📂', help_text="Icono emoji o clase CSS")
    display_order = models.IntegerField(default=0, help_text="Orden de presentación")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accounts'
        db_table = 'families'
        ordering = ['display_order', 'name']
        unique_together = [('module', 'name')]

    def __str__(self):
        return f"{self.module.name} / {self.name}"
