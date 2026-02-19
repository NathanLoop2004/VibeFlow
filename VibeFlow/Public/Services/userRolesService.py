"""
userRolesService.py - Capa de servicio para las consultas SQL de asignación de roles.
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


def get_all_user_roles():
    """Obtiene todas las asignaciones user-role con JOIN a users y roles."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                ur.user_id,
                u.username,
                ur.role_id,
                r.name AS role_name
            FROM app.user_roles ur
            JOIN app.users u ON u.id = ur.user_id
            JOIN app.roles r ON r.id = ur.role_id
            ORDER BY u.username, r.name
        """)
        rows = _dictfetchall(cursor)
        for r in rows:
            r['user_id'] = str(r['user_id'])
        return rows


def get_roles_by_user(user_id):
    """Obtiene todos los roles asignados a un usuario."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                r.id AS role_id,
                r.name AS role_name
            FROM app.user_roles ur
            JOIN app.roles r ON r.id = ur.role_id
            WHERE ur.user_id = %s
            ORDER BY r.name
        """, [user_id])
        return _dictfetchall(cursor)


def get_users_by_role(role_id):
    """Obtiene todos los usuarios que tienen un rol específico."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                u.id AS user_id,
                u.username
            FROM app.user_roles ur
            JOIN app.users u ON u.id = ur.user_id
            WHERE ur.role_id = %s
            ORDER BY u.username
        """, [role_id])
        rows = _dictfetchall(cursor)
        for r in rows:
            r['user_id'] = str(r['user_id'])
        return rows


def assign_role(data):
    """Asigna un rol a un usuario. Recibe dict con: user_id, role_id."""
    user_id = data["user_id"]
    role_id = data["role_id"]

    with connection.cursor() as cursor:
        # Verificar si ya tiene el rol asignado
        cursor.execute("""
            SELECT 1 FROM app.user_roles
            WHERE user_id = %s AND role_id = %s
        """, [user_id, role_id])

        if cursor.fetchone():
            raise ValueError("El usuario ya tiene este rol asignado")

        cursor.execute("""
            INSERT INTO app.user_roles (user_id, role_id)
            VALUES (%s, %s)
        """, [user_id, role_id])

        return {"message": "Rol asignado exitosamente"}


def remove_role(user_id, role_id):
    """Elimina la asignación de un rol a un usuario. Retorna True/False."""
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM app.user_roles
            WHERE user_id = %s AND role_id = %s
        """, [user_id, role_id])
        return cursor.rowcount > 0


def user_has_role(user_id, role_id):
    """Verifica si un usuario tiene un rol específico."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 1 FROM app.user_roles
            WHERE user_id = %s AND role_id = %s
        """, [user_id, role_id])
        return cursor.fetchone() is not None
