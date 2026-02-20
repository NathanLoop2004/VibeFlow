"""
songsService.py - Capa de servicio para canciones del Shazam MVP.
CRUD + integración con fingerprintService.
"""

import base64
from django.db import connection


def _dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _dictfetchone(cursor):
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


def get_all_songs():
    """Obtiene todas las canciones (sin audio_data)."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, artist, duration_seconds, file_type,
                   file_size, fingerprint_count, created_at
            FROM app.songs
            ORDER BY created_at DESC
        """)
        rows = _dictfetchall(cursor)
        for r in rows:
            r['created_at'] = r['created_at'].isoformat() if r['created_at'] else None
        return rows


def get_song_by_id(song_id):
    """Obtiene una canción por ID (sin audio_data)."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, artist, duration_seconds, file_type,
                   file_size, fingerprint_count, created_at
            FROM app.songs WHERE id = %s
        """, [song_id])
        row = _dictfetchone(cursor)
        if row:
            row['created_at'] = row['created_at'].isoformat() if row['created_at'] else None
        return row


def create_song(data):
    """
    Crea una canción.
    data: title, artist, duration_seconds, file_type, file_size, audio_base64
    """
    audio_bytes = None
    if data.get('audio_base64'):
        audio_bytes = base64.b64decode(data['audio_base64'])

    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO app.songs
                (title, artist, duration_seconds, file_type, file_size, audio_data, fingerprint_count, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, 0, NOW(), NOW())
            RETURNING id
        """, [
            data['title'],
            data.get('artist', 'Desconocido'),
            data.get('duration_seconds'),
            data.get('file_type', 'audio/wav'),
            data.get('file_size'),
            audio_bytes,
        ])
        row = cursor.fetchone()
        return {"id": row[0], "message": "Canción creada exitosamente"}


def delete_song(song_id):
    """Elimina una canción y sus fingerprints (CASCADE)."""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM app.songs WHERE id = %s RETURNING id", [song_id])
        row = cursor.fetchone()
        if not row:
            raise ValueError("Canción no encontrada")
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
    """Obtiene los datos de audio de una canción."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT audio_data, file_type, title, artist
            FROM app.songs WHERE id = %s
        """, [song_id])
        row = _dictfetchone(cursor)
        if row and row['audio_data']:
            row['audio_data'] = bytes(row['audio_data'])
        return row
