"""
subfamiliesModel.py - Modelo para subfamilias (tercer nivel del menú).
Cada subfamilia pertenece a una familia.
"""

from django.db import models


class Subfamily(models.Model):
    id = models.AutoField(primary_key=True)
    family = models.ForeignKey(
        'accounts.Family',
        on_delete=models.CASCADE,
        related_name='subfamilies',
        help_text="Familia a la que pertenece"
    )
    name = models.CharField(max_length=100, help_text="Nombre de la subfamilia")
    icon = models.CharField(max_length=50, default='📄', help_text="Icono emoji o clase CSS")
    display_order = models.IntegerField(default=0, help_text="Orden de presentación")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accounts'
        db_table = 'subfamilies'
        ordering = ['display_order', 'name']
        unique_together = [('family', 'name')]

    def __str__(self):
        return f"{self.family.name} / {self.name}"
