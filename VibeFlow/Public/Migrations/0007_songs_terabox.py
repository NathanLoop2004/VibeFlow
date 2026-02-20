"""
0007_songs_terabox.py - Migración para mover audio a TeraBox.

Cambia la columna audio_data por terabox_path.
El audio binario ya no se almacena en la BD; se sube a TeraBox y solo
se guarda la ruta remota.

Usa SQL directo porque la tabla vive en el schema 'app'.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_songs_fingerprints'),
    ]

    operations = [
        # SQL real contra la BD (schema app)
        migrations.RunSQL(
            sql="ALTER TABLE app.songs ADD COLUMN IF NOT EXISTS terabox_path VARCHAR(500) NULL;",
            reverse_sql="ALTER TABLE app.songs DROP COLUMN IF EXISTS terabox_path;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE app.songs DROP COLUMN IF EXISTS audio_data;",
            reverse_sql="ALTER TABLE app.songs ADD COLUMN audio_data BYTEA NULL;",
        ),
        # Actualizar estado interno de Django (sin tocar la BD)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='song',
                    name='audio_data',
                ),
                migrations.AddField(
                    model_name='song',
                    name='terabox_path',
                    field=models.CharField(
                        blank=True,
                        help_text='Ruta del audio en TeraBox',
                        max_length=500,
                        null=True,
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
