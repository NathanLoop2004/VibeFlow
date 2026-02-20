"""
fingerprintsModel.py - Modelo para fingerprints de audio (Shazam MVP).
Cada fingerprint es un hash derivado de picos espectrales.
"""

from django.db import models


class Fingerprint(models.Model):
    song = models.ForeignKey(
        'accounts.Song', on_delete=models.CASCADE,
        related_name='fingerprints',
        help_text="Canción a la que pertenece este fingerprint"
    )
    hash = models.CharField(max_length=40, db_index=True, help_text="SHA-1 hash del pico espectral")
    time_offset = models.IntegerField(help_text="Offset temporal en frames desde el inicio")

    class Meta:
        app_label = 'accounts'
        db_table = 'fingerprints'
        indexes = [
            models.Index(fields=['hash'], name='idx_fingerprint_hash'),
        ]

    def __str__(self):
        return f"FP(song={self.song_id}, t={self.time_offset})"
