"""
songsService.py - Capa de servicio para canciones del Shazam MVP.
CRUD + integración con TeraBox para almacenamiento de audio.

El audio binario ya NO se guarda en la BD.
Se sube a TeraBox y se almacena solo la ruta remota (terabox_path).
Los fingerprints (hashes) sí permanecen en Postgres.
"""

from django.db import connection
from VibeFlow.Public.Services import teraboxService


def _dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _dictfetchone(cursor):
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


def get_all_songs():
    """Obtiene todas las canciones (metadatos)."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, artist, duration_seconds, file_type,
                   file_size, fingerprint_count, terabox_path, created_at
            FROM app.songs
            ORDER BY created_at DESC
        """)
        rows = _dictfetchall(cursor)
        for r in rows:
            r['created_at'] = r['created_at'].isoformat() if r['created_at'] else None
            r['has_audio'] = bool(r.get('terabox_path'))
        return rows


def get_song_by_id(song_id):
    """Obtiene una canción por ID (metadatos)."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, artist, duration_seconds, file_type,
                   file_size, fingerprint_count, terabox_path, created_at
            FROM app.songs WHERE id = %s
        """, [song_id])
        row = _dictfetchone(cursor)
        if row:
            row['created_at'] = row['created_at'].isoformat() if row['created_at'] else None
            row['has_audio'] = bool(row.get('terabox_path'))
        return row


def create_song(data, terabox_path=None):
    """
    Crea una canción en la BD.
    data: title, artist, duration_seconds, file_type, file_size
    terabox_path: ruta del audio en TeraBox (opcional, se sube por separado)
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO app.songs
                (title, artist, duration_seconds, file_type, file_size,
                 terabox_path, fingerprint_count, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, 0, NOW(), NOW())
            RETURNING id
        """, [
            data['title'],
            data.get('artist', 'Desconocido'),
            data.get('duration_seconds'),
            data.get('file_type', 'audio/wav'),
            data.get('file_size'),
            terabox_path,
        ])
        row = cursor.fetchone()
        return {"id": row[0], "message": "Canción creada exitosamente"}


def update_terabox_path(song_id, terabox_path):
    """Actualiza la ruta de TeraBox de una canción."""
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE app.songs
            SET terabox_path = %s, updated_at = NOW()
            WHERE id = %s
        """, [terabox_path, song_id])


def delete_song(song_id):
    """Elimina una canción, sus fingerprints y su audio de TeraBox."""
    # Obtener terabox_path antes de borrar
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT terabox_path FROM app.songs WHERE id = %s", [song_id]
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError("Canción no encontrada")
        terabox_path = row[0]

    # Eliminar de TeraBox (si tiene audio)
    if terabox_path:
        try:
            teraboxService.delete_song(terabox_path)
        except Exception as e:
            print(f"[TeraBox] Error eliminando {terabox_path}: {e}")

    # Eliminar de BD (CASCADE borra fingerprints)
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM app.songs WHERE id = %s", [song_id])
    return True


def update_song(song_id, data):
    """Actualiza título y artista."""
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE app.songs
            SET title = %s, artist = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING id
        """, [data['title'], data.get('artist', 'Desconocido'), song_id])
        row = cursor.fetchone()
        if not row:
            raise ValueError("Canción no encontrada")
        return {"id": row[0], "message": "Canción actualizada"}


def get_song_audio(song_id):
    """
    Obtiene los datos de audio descargándolos de TeraBox.
    Retorna dict con audio_data (bytes), file_type, title, artist.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT terabox_path, file_type, title, artist
            FROM app.songs WHERE id = %s
        """, [song_id])
        row = _dictfetchone(cursor)

    if not row or not row.get('terabox_path'):
        return None

    # Descargar de TeraBox
    audio_bytes = teraboxService.download_song(row['terabox_path'])
    return {
        'audio_data': audio_bytes,
        'file_type':  row['file_type'],
        'title':      row['title'],
        'artist':     row['artist'],
    }


def get_song_terabox_path(song_id):
    """Obtiene solo la ruta TeraBox de una canción."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, title, terabox_path FROM app.songs WHERE id = %s",
            [song_id],
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {'id': row[0], 'title': row[1], 'terabox_path': row[2]}
