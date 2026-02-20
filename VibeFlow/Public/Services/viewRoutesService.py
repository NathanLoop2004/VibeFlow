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
    """Obtiene todas las rutas con info de módulo/familia/subfamilia."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                vr.id,
                vr.url_path,
                vr.template_name,
                vr.name,
                vr.is_active,
                vr.module_id,
                m.name AS module_name,
                vr.family_id,
                f.name AS family_name,
                vr.subfamily_id,
                sf.name AS subfamily_name,
                vr.created_at
            FROM app.view_routes vr
            LEFT JOIN app.modules m ON m.id = vr.module_id
            LEFT JOIN app.families f ON f.id = vr.family_id
            LEFT JOIN app.subfamilies sf ON sf.id = vr.subfamily_id
            ORDER BY vr.url_path ASC
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
    """Crea una nueva ruta. Recibe dict con: url_path, template_name, name, module_id, family_id, subfamily_id."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO app.view_routes (url_path, template_name, name, is_active, module_id, family_id, subfamily_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, [
            data["url_path"],
            data["template_name"],
            data["name"],
            data.get("is_active", True),
            data.get("module_id") or None,
            data.get("family_id") or None,
            data.get("subfamily_id") or None,
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
    if "module_id" in data:
        fields.append("module_id = %s")
        values.append(data["module_id"] or None)
    if "family_id" in data:
        fields.append("family_id = %s")
        values.append(data["family_id"] or None)
    if "subfamily_id" in data:
        fields.append("subfamily_id = %s")
        values.append(data["subfamily_id"] or None)

    if not fields:
        return None

    fields.append("updated_at = NOW()")
    values.append(route_id)

    with connection.cursor() as cursor:
        cursor.execute(f"""
            UPDATE app.view_routes
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING id, url_path, template_name, name, is_active, module_id, family_id, subfamily_id
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
