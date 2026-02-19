"""
usersService.py - Capa de servicio para las consultas SQL de usuarios.
Consultas SQL directas usando django.db.connection.
"""

import uuid
from django.db import connection
import bcrypt as _bcrypt


def _hash_password(password):
    """Hash a password using bcrypt."""
    return _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')


def _verify_password(password, hashed):
    """Verify a password against a bcrypt hash."""
    return _bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def _dictfetchall(cursor):
    """Convierte las filas del cursor en una lista de dicts."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _dictfetchone(cursor):
    """Convierte una fila del cursor en dict. Retorna None si no hay resultado."""
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


def get_all_users():
    """Obtiene todos los usuarios ordenados por fecha de creación."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                id,
                username,
                email,
                is_active,
                is_verified,
                is_superuser,
                created_at
            FROM app.users
            ORDER BY created_at DESC
        """)
        rows = _dictfetchall(cursor)
        for r in rows:
            r['id'] = str(r['id'])
            r['created_at'] = r['created_at'].isoformat() if r['created_at'] else None
        return rows


def get_user_by_id(user_id):
    """Obtiene un usuario por su UUID. Retorna None si no existe."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                id, username, email,
                is_active, is_verified, is_superuser,
                created_at
            FROM app.users
            WHERE id = %s
        """, [user_id])
        row = _dictfetchone(cursor)
        if row:
            row['id'] = str(row['id'])
            row['created_at'] = row['created_at'].isoformat() if row['created_at'] else None
        return row


def create_user(data):
    """Crea un nuevo usuario. Recibe dict con: username, email, password."""
    password = data.get("password", "")
    password_hash = _hash_password(password)
    new_id = str(uuid.uuid4())

    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO app.users (id, username, email, password_hash, is_active, is_verified, is_superuser)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, [
            new_id,
            data["username"],
            data["email"],
            password_hash,
            data.get("is_active", True),
            data.get("is_verified", False),
            data.get("is_superuser", False),
        ])
        row = cursor.fetchone()
        return {"id": str(row[0]), "message": "Usuario creado exitosamente"}


def delete_user(user_id):
    """Elimina un usuario por su UUID. Retorna True si fue eliminado."""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM app.users WHERE id = %s", [user_id])
        return cursor.rowcount > 0


def update_user(user_id, data):
    """Actualiza los campos de un usuario."""
    fields = []
    values = []

    if "username" in data:
        fields.append("username = %s")
        values.append(data["username"])
    if "email" in data:
        fields.append("email = %s")
        values.append(data["email"])
    if "password" in data:
        fields.append("password_hash = %s")
        values.append(_hash_password(data["password"]))
    if "is_active" in data:
        fields.append("is_active = %s")
        values.append(data["is_active"])
    if "is_verified" in data:
        fields.append("is_verified = %s")
        values.append(data["is_verified"])
    if "is_superuser" in data:
        fields.append("is_superuser = %s")
        values.append(data["is_superuser"])

    if not fields:
        return None

    values.append(user_id)

    with connection.cursor() as cursor:
        cursor.execute(f"""
            UPDATE app.users
            SET {', '.join(fields)}, updated_at = NOW()
            WHERE id = %s
            RETURNING id, username, email
        """, values)
        row = _dictfetchone(cursor)
        if row:
            row['id'] = str(row['id'])
            row['message'] = "Usuario actualizado exitosamente"
        return row


def get_user_by_username(username):
    """Busca un usuario por su username."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, username, email, is_active
            FROM app.users
            WHERE username = %s
        """, [username])
        row = _dictfetchone(cursor)
        if row:
            row['id'] = str(row['id'])
        return row


def get_user_by_email(email):
    """Busca un usuario por su email."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, username, email, is_active
            FROM app.users
            WHERE email = %s
        """, [email])
        row = _dictfetchone(cursor)
        if row:
            row['id'] = str(row['id'])
        return row


def authenticate_user(username, password):
    """
    Autentica un usuario por username y password.
    Retorna el usuario (dict) si las credenciales son válidas, None si no.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, username, email, password_hash, is_active, is_verified, is_superuser
            FROM app.users
            WHERE username = %s
        """, [username])
        row = _dictfetchone(cursor)

    if not row:
        return None

    if not _verify_password(password, row['password_hash']):
        return None

    if not row['is_active']:
        return None

    # No retornar el hash al frontend
    del row['password_hash']
    row['id'] = str(row['id'])
    return row
