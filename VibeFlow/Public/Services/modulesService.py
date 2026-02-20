"""
modulesService.py - Capa de servicio para módulos.
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


def get_all_modules():
    """Obtiene todos los módulos ordenados por display_order."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, icon, display_order, is_active, created_at
            FROM app.modules
            ORDER BY display_order ASC, name ASC
        """)
        rows = _dictfetchall(cursor)
        for r in rows:
            r['created_at'] = r['created_at'].isoformat() if r['created_at'] else None
        return rows


def get_active_modules():
    """Obtiene solo los módulos activos."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, icon, display_order
            FROM app.modules
            WHERE is_active = TRUE
            ORDER BY display_order ASC, name ASC
        """)
        return _dictfetchall(cursor)


def create_module(data):
    """Crea un nuevo módulo."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO app.modules (name, icon, display_order, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, [
            data["name"],
            data.get("icon", "📁"),
            data.get("display_order", 0),
            data.get("is_active", True),
        ])
        row = cursor.fetchone()
        return {"id": row[0], "message": "Módulo creado exitosamente"}


def update_module(module_id, data):
    """Actualiza un módulo."""
    fields = []
    values = []

    if "name" in data:
        fields.append("name = %s")
        values.append(data["name"])
    if "icon" in data:
        fields.append("icon = %s")
        values.append(data["icon"])
    if "display_order" in data:
        fields.append("display_order = %s")
        values.append(data["display_order"])
    if "is_active" in data:
        fields.append("is_active = %s")
        values.append(data["is_active"])

    if not fields:
        return None

    fields.append("updated_at = NOW()")
    values.append(module_id)

    with connection.cursor() as cursor:
        cursor.execute(f"""
            UPDATE app.modules
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING id, name, icon, display_order, is_active
        """, values)
        return _dictfetchone(cursor)


def delete_module(module_id):
    """Elimina un módulo por su ID."""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM app.modules WHERE id = %s", [module_id])
        return cursor.rowcount > 0
