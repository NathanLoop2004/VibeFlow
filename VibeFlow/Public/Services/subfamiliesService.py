"""
subfamiliesService.py - Capa de servicio para subfamilias.
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


def get_all_subfamilies():
    """Obtiene todas las subfamilias con nombre de la familia y módulo."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                sf.id,
                sf.family_id,
                f.name AS family_name,
                f.module_id,
                m.name AS module_name,
                sf.name,
                sf.icon,
                sf.display_order,
                sf.is_active,
                sf.created_at
            FROM app.subfamilies sf
            JOIN app.families f ON f.id = sf.family_id
            JOIN app.modules m ON m.id = f.module_id
            ORDER BY m.display_order, f.display_order, sf.display_order, sf.name
        """)
        rows = _dictfetchall(cursor)
        for r in rows:
            r['created_at'] = r['created_at'].isoformat() if r['created_at'] else None
        return rows


def get_subfamilies_by_family(family_id):
    """Obtiene subfamilias de una familia específica."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, family_id, name, icon, display_order, is_active
            FROM app.subfamilies
            WHERE family_id = %s AND is_active = TRUE
            ORDER BY display_order ASC, name ASC
        """, [family_id])
        return _dictfetchall(cursor)


def create_subfamily(data):
    """Crea una nueva subfamilia."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO app.subfamilies (family_id, name, icon, display_order, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, [
            data["family_id"],
            data["name"],
            data.get("icon", "📄"),
            data.get("display_order", 0),
            data.get("is_active", True),
        ])
        row = cursor.fetchone()
        return {"id": row[0], "message": "Subfamilia creada exitosamente"}


def update_subfamily(sf_id, data):
    """Actualiza una subfamilia."""
    fields = []
    values = []

    if "family_id" in data:
        fields.append("family_id = %s")
        values.append(data["family_id"])
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
    values.append(sf_id)

    with connection.cursor() as cursor:
        cursor.execute(f"""
            UPDATE app.subfamilies
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING id, family_id, name, icon, display_order, is_active
        """, values)
        return _dictfetchone(cursor)


def delete_subfamily(sf_id):
    """Elimina una subfamilia por su ID."""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM app.subfamilies WHERE id = %s", [sf_id])
        return cursor.rowcount > 0
