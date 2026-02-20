"""
0007_songs_terabox.py - Migración para mover audio a TeraBox.

Cambia la columna audio_data por terabox_path.
El audio binario ya no se almacena en la BD; se sube a TeraBox y solo
se guarda la ruta remota.

Usa SQL directo porque la tabla vive en el schema 'app'.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_songs_fingerprints'),
    ]

    operations = [
        # 1. Añadir columna terabox_path
        migrations.RunSQL(
            sql="ALTER TABLE app.songs ADD COLUMN IF NOT EXISTS terabox_path VARCHAR(500) NULL;",
            reverse_sql="ALTER TABLE app.songs DROP COLUMN IF EXISTS terabox_path;",
        ),
        # 2. Eliminar columna audio_data (liberar almacenamiento)
        migrations.RunSQL(
            sql="ALTER TABLE app.songs DROP COLUMN IF EXISTS audio_data;",
            reverse_sql="ALTER TABLE app.songs ADD COLUMN audio_data BYTEA NULL;",
        ),
    ]
