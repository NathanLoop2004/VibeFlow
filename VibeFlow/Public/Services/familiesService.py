"""
familiesService.py - Capa de servicio para familias.
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


def get_all_families():
    """Obtiene todas las familias con nombre del módulo."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                f.id,
                f.module_id,
                m.name AS module_name,
                f.name,
                f.icon,
                f.display_order,
                f.is_active,
                f.created_at
            FROM app.families f
            JOIN app.modules m ON m.id = f.module_id
            ORDER BY m.display_order, f.display_order, f.name
        """)
        rows = _dictfetchall(cursor)
        for r in rows:
            r['created_at'] = r['created_at'].isoformat() if r['created_at'] else None
        return rows


def get_families_by_module(module_id):
    """Obtiene familias de un módulo específico."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, module_id, name, icon, display_order, is_active
            FROM app.families
            WHERE module_id = %s AND is_active = TRUE
            ORDER BY display_order ASC, name ASC
        """, [module_id])
        return _dictfetchall(cursor)


def create_family(data):
    """Crea una nueva familia."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO app.families (module_id, name, icon, display_order, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, [
            data["module_id"],
            data["name"],
            data.get("icon", "📂"),
            data.get("display_order", 0),
            data.get("is_active", True),
        ])
        row = cursor.fetchone()
        return {"id": row[0], "message": "Familia creada exitosamente"}


def update_family(family_id, data):
    """Actualiza una familia."""
    fields = []
    values = []

    if "module_id" in data:
        fields.append("module_id = %s")
        values.append(data["module_id"])
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
    values.append(family_id)

    with connection.cursor() as cursor:
        cursor.execute(f"""
            UPDATE app.families
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING id, module_id, name, icon, display_order, is_active
        """, values)
        return _dictfetchone(cursor)


def delete_family(family_id):
    """Elimina una familia por su ID."""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM app.families WHERE id = %s", [family_id])
        return cursor.rowcount > 0
