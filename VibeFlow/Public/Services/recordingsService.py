"""
recordingsService.py - Capa de servicio para grabaciones de audio.
Consultas SQL directas usando django.db.connection.
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


def get_all_recordings():
    """Obtiene todas las grabaciones (sin audio_data para listar)."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                r.id, r.user_id, r.name, r.duration_seconds,
                r.sample_rate, r.file_type, r.file_size,
                r.created_at, r.updated_at,
                u.username
            FROM app.recordings r
            LEFT JOIN app.users u ON u.id = r.user_id
            ORDER BY r.created_at DESC
        """)
        rows = _dictfetchall(cursor)
        for r in rows:
            r['user_id'] = str(r['user_id'])
            r['created_at'] = r['created_at'].isoformat() if r['created_at'] else None
            r['updated_at'] = r['updated_at'].isoformat() if r['updated_at'] else None
        return rows


def get_recordings_by_user(user_id):
    """Obtiene las grabaciones de un usuario (sin audio_data)."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                id, user_id, name, duration_seconds,
                sample_rate, file_type, file_size,
                created_at, updated_at
            FROM app.recordings
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, [user_id])
        rows = _dictfetchall(cursor)
        for r in rows:
            r['user_id'] = str(r['user_id'])
            r['created_at'] = r['created_at'].isoformat() if r['created_at'] else None
            r['updated_at'] = r['updated_at'].isoformat() if r['updated_at'] else None
        return rows


def get_recording_by_id(recording_id):
    """Obtiene una grabación por ID (sin audio_data)."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                r.id, r.user_id, r.name, r.duration_seconds,
                r.sample_rate, r.file_type, r.file_size,
                r.created_at, r.updated_at,
                u.username
            FROM app.recordings r
            LEFT JOIN app.users u ON u.id = r.user_id
            WHERE r.id = %s
        """, [recording_id])
        row = _dictfetchone(cursor)
        if row:
            row['user_id'] = str(row['user_id'])
            row['created_at'] = row['created_at'].isoformat() if row['created_at'] else None
            row['updated_at'] = row['updated_at'].isoformat() if row['updated_at'] else None
        return row


def get_recording_audio(recording_id):
    """Obtiene los datos de audio de una grabación (para descargar/reproducir)."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT audio_data, file_type, name
            FROM app.recordings
            WHERE id = %s
        """, [recording_id])
        row = _dictfetchone(cursor)
        if row and row['audio_data']:
            row['audio_data'] = bytes(row['audio_data'])
        return row


def create_recording(data):
    """
    Crea una nueva grabación.
    data: user_id, name, duration_seconds, sample_rate, audio_base64, file_type, file_size
    """
    audio_bytes = None
    if data.get('audio_base64'):
        audio_bytes = base64.b64decode(data['audio_base64'])

    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO app.recordings
                (user_id, name, duration_seconds, sample_rate, audio_data, file_type, file_size, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, [
            data['user_id'],
            data['name'],
            data.get('duration_seconds'),
            data.get('sample_rate', 44100),
            audio_bytes,
            data.get('file_type', 'audio/webm'),
            data.get('file_size'),
        ])
        row = cursor.fetchone()
        return {"id": row[0], "message": "Grabación guardada exitosamente"}


def update_recording(recording_id, data):
    """Actualiza el nombre de una grabación."""
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE app.recordings
            SET name = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING id
        """, [data['name'], recording_id])
        row = cursor.fetchone()
        if not row:
            raise ValueError("Grabación no encontrada")
        return {"id": row[0], "message": "Grabación actualizada"}


def delete_recording(recording_id):
    """Elimina una grabación."""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM app.recordings WHERE id = %s RETURNING id", [recording_id])
        row = cursor.fetchone()
        if not row:
            raise ValueError("Grabación no encontrada")
        return True
