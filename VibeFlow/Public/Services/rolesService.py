"""
rolesService.py - Capa de servicio para las consultas SQL de roles.
Consultas SQL directas usando django.db.connection.
"""

from django.db import connection


def _dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _dictfetchone(cursor):
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


def get_all_roles():
    """Obtiene todos los roles ordenados por ID."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, description
            FROM app.roles
            ORDER BY id ASC
        """)
        return _dictfetchall(cursor)


def get_role_by_id(role_id):
    """Obtiene un rol por su ID. Retorna None si no existe."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, description
            FROM app.roles
            WHERE id = %s
        """, [role_id])
        return _dictfetchone(cursor)


def create_role(data):
    """Crea un nuevo rol. Recibe dict con: name, description."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO app.roles (name, description)
            VALUES (%s, %s)
            RETURNING id
        """, [data["name"], data.get("description", "")])
        row = cursor.fetchone()
        return {"id": row[0], "message": "Rol creado exitosamente"}


def delete_role(role_id):
    """Elimina un rol por su ID. Retorna True si fue eliminado."""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM app.roles WHERE id = %s", [role_id])
        return cursor.rowcount > 0


def update_role(role_id, data):
    """Actualiza los campos de un rol."""
    fields = []
    values = []

    if "name" in data:
        fields.append("name = %s")
        values.append(data["name"])
    if "description" in data:
        fields.append("description = %s")
        values.append(data["description"])

    if not fields:
        return None

    values.append(role_id)

    with connection.cursor() as cursor:
        cursor.execute(f"""
            UPDATE app.roles
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING id, name
        """, values)
        row = _dictfetchone(cursor)
        if row:
            row['message'] = "Rol actualizado exitosamente"
        return row


def get_role_by_name(name):
    """Busca un rol por su nombre."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, description
            FROM app.roles
            WHERE name = %s
        """, [name])
        return _dictfetchone(cursor)
