"""
viewRoutesService.py - Capa de servicio para las consultas SQL de rutas de vistas.
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


def get_all_routes():
    """Obtiene todas las rutas ordenadas por url_path."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                id,
                url_path,
                template_name,
                name,
                is_active,
                created_at
            FROM app.view_routes
            ORDER BY url_path ASC
        """)
        rows = _dictfetchall(cursor)
        for r in rows:
            r['created_at'] = r['created_at'].isoformat() if r['created_at'] else None
        return rows


def get_active_routes():
    """Obtiene solo las rutas activas (is_active=True)."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, url_path, template_name, name
            FROM app.view_routes
            WHERE is_active = TRUE
            ORDER BY url_path ASC
        """)
        return _dictfetchall(cursor)


def get_route_by_path(url_path):
    """Busca una ruta activa por su url_path. Retorna dict o None."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, url_path, template_name, name, is_active
            FROM app.view_routes
            WHERE url_path = %s AND is_active = TRUE
        """, [url_path])
        return _dictfetchone(cursor)


def create_route(data):
    """Crea una nueva ruta. Recibe dict con: url_path, template_name, name."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO app.view_routes (url_path, template_name, name, is_active)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, [
            data["url_path"],
            data["template_name"],
            data["name"],
            data.get("is_active", True),
        ])
        row = cursor.fetchone()
        return {"id": row[0], "message": "Ruta creada exitosamente"}


def delete_route(route_id):
    """Elimina una ruta por su ID. Retorna True/False."""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM app.view_routes WHERE id = %s", [route_id])
        return cursor.rowcount > 0


def update_route(route_id, data):
    """Actualiza los campos de una ruta."""
    fields = []
    values = []

    if "url_path" in data:
        fields.append("url_path = %s")
        values.append(data["url_path"])
    if "template_name" in data:
        fields.append("template_name = %s")
        values.append(data["template_name"])
    if "name" in data:
        fields.append("name = %s")
        values.append(data["name"])
    if "is_active" in data:
        fields.append("is_active = %s")
        values.append(data["is_active"])

    if not fields:
        return None

    fields.append("updated_at = NOW()")
    values.append(route_id)

    with connection.cursor() as cursor:
        cursor.execute(f"""
            UPDATE app.view_routes
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING id, url_path, template_name, name, is_active
        """, values)
        return _dictfetchone(cursor)


def toggle_route(route_id):
    """Activa/desactiva una ruta."""
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE app.view_routes
            SET is_active = NOT is_active, updated_at = NOW()
            WHERE id = %s
            RETURNING id, is_active
        """, [route_id])
        return _dictfetchone(cursor)
