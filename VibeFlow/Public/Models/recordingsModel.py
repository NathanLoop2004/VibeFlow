"""
recordingsModel.py - Modelo para almacenar grabaciones de audio con datos de espectrograma.
Cada registro representa una grabación capturada desde el micrófono o subida como archivo.
"""

from django.db import models


class Recording(models.Model):
    user_id = models.UUIDField(help_text="ID del usuario que realizó la grabación")
    name = models.CharField(max_length=255, help_text="Nombre descriptivo de la grabación")
    duration_seconds = models.FloatField(null=True, blank=True, help_text="Duración en segundos")
    sample_rate = models.IntegerField(default=44100, help_text="Frecuencia de muestreo en Hz")
    audio_data = models.BinaryField(null=True, blank=True, help_text="Datos de audio en formato binario")
    file_type = models.CharField(max_length=50, default='audio/webm', help_text="MIME type del audio")
    file_size = models.IntegerField(null=True, blank=True, help_text="Tamaño del archivo en bytes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accounts'
        db_table = 'recordings'
        ordering = ['-created_at']

    def __str__(self):
        return f"Recording({self.id}: {self.name})"
