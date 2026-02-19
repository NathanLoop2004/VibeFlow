"""
routePermissionsService.py - Capa de servicio para los permisos de rutas.
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


def get_all_permissions():
    """Obtiene todos los permisos con JOIN a users y view_routes."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                rp.id,
                rp.user_id,
                u.username,
                rp.route_id,
                vr.url_path,
                vr.name AS route_name,
                rp.can_get,
                rp.can_post,
                rp.can_put,
                rp.can_delete
            FROM app.route_permissions rp
            JOIN app.users u ON u.id = rp.user_id
            JOIN app.view_routes vr ON vr.id = rp.route_id
            ORDER BY vr.url_path, u.username
        """)
        rows = _dictfetchall(cursor)
        for r in rows:
            r['user_id'] = str(r['user_id'])
        return rows


def get_permissions_by_route(route_id):
    """Obtiene todos los usuarios con permisos para una ruta específica."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                rp.id,
                rp.user_id,
                u.username,
                rp.can_get,
                rp.can_post,
                rp.can_put,
                rp.can_delete
            FROM app.route_permissions rp
            JOIN app.users u ON u.id = rp.user_id
            WHERE rp.route_id = %s
            ORDER BY u.username
        """, [route_id])
        rows = _dictfetchall(cursor)
        for r in rows:
            r['user_id'] = str(r['user_id'])
        return rows


def get_permissions_by_user(user_id):
    """Obtiene todas las rutas a las que tiene acceso un usuario."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                rp.id,
                rp.route_id,
                vr.url_path,
                vr.name AS route_name,
                rp.can_get,
                rp.can_post,
                rp.can_put,
                rp.can_delete
            FROM app.route_permissions rp
            JOIN app.view_routes vr ON vr.id = rp.route_id
            WHERE rp.user_id = %s
            ORDER BY vr.url_path
        """, [user_id])
        return _dictfetchall(cursor)


def create_permission(data):
    """Asigna permisos a un usuario para una ruta."""
    user_id = data["user_id"]
    route_id = data["route_id"]

    with connection.cursor() as cursor:
        # Verificar si ya existe
        cursor.execute("""
            SELECT 1 FROM app.route_permissions
            WHERE user_id = %s AND route_id = %s
        """, [user_id, route_id])

        if cursor.fetchone():
            raise ValueError("Este usuario ya tiene permisos configurados para esta ruta")

        cursor.execute("""
            INSERT INTO app.route_permissions (user_id, route_id, can_get, can_post, can_put, can_delete)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, [
            user_id,
            route_id,
            data.get("can_get", False),
            data.get("can_post", False),
            data.get("can_put", False),
            data.get("can_delete", False),
        ])
        row = cursor.fetchone()
        return {"id": row[0], "message": "Permisos asignados exitosamente"}


def update_permission(perm_id, data):
    """Actualiza los métodos permitidos de un permiso existente."""
    fields = []
    values = []

    if "can_get" in data:
        fields.append("can_get = %s")
        values.append(data["can_get"])
    if "can_post" in data:
        fields.append("can_post = %s")
        values.append(data["can_post"])
    if "can_put" in data:
        fields.append("can_put = %s")
        values.append(data["can_put"])
    if "can_delete" in data:
        fields.append("can_delete = %s")
        values.append(data["can_delete"])

    if not fields:
        return None

    fields.append("updated_at = NOW()")
    values.append(perm_id)

    with connection.cursor() as cursor:
        cursor.execute(f"""
            UPDATE app.route_permissions
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING id, can_get, can_post, can_put, can_delete
        """, values)
        row = _dictfetchone(cursor)
        if row:
            row['message'] = "Permisos actualizados"
        return row


def delete_permission(perm_id):
    """Elimina un permiso. Retorna True/False."""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM app.route_permissions WHERE id = %s", [perm_id])
        return cursor.rowcount > 0


def check_permission(user_id, url_path, method):
    """
    Verifica si un usuario tiene permiso para un método HTTP en una ruta.
    Retorna True si tiene permiso, False si no.
    """
    method_col = {
        'GET': 'can_get',
        'POST': 'can_post',
        'PUT': 'can_put',
        'DELETE': 'can_delete',
    }.get(method.upper())

    if not method_col:
        return False

    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT rp.{method_col}
            FROM app.route_permissions rp
            JOIN app.view_routes vr ON vr.id = rp.route_id
            WHERE rp.user_id = %s
              AND vr.url_path = %s
              AND vr.is_active = TRUE
        """, [user_id, url_path])
        row = cursor.fetchone()
        return bool(row and row[0])
