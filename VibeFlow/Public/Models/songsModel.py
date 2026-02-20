"""
songsModel.py - Modelo para canciones del sistema Shazam MVP.
"""

from django.db import models


class Song(models.Model):
    title = models.CharField(max_length=255, help_text="Título de la canción")
    artist = models.CharField(max_length=255, default='Desconocido', help_text="Artista")
    duration_seconds = models.FloatField(null=True, blank=True, help_text="Duración en segundos")
    file_type = models.CharField(max_length=50, default='audio/mpeg', help_text="MIME type")
    file_size = models.IntegerField(null=True, blank=True, help_text="Tamaño en bytes")
    audio_data = models.BinaryField(null=True, blank=True, help_text="Audio original (binario)")
    fingerprint_count = models.IntegerField(default=0, help_text="Cantidad de fingerprints generados")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accounts'
        db_table = 'songs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.artist}"
