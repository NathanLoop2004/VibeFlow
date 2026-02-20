"""
routePermissionsService.py - Capa de servicio para los permisos de rutas.
Los permisos se asignan por ROL (no por usuario).
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
    """Obtiene todos los permisos con JOIN a roles y view_routes."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                rp.id,
                rp.role_id,
                r.name AS role_name,
                rp.route_id,
                vr.url_path,
                vr.name AS route_name,
                rp.can_get,
                rp.can_post,
                rp.can_put,
                rp.can_delete
            FROM app.route_permissions rp
            JOIN app.roles r ON r.id = rp.role_id
            JOIN app.view_routes vr ON vr.id = rp.route_id
            ORDER BY r.name, vr.url_path
        """)
        return _dictfetchall(cursor)


def get_permissions_by_route(route_id):
    """Obtiene todos los roles con permisos para una ruta específica."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                rp.id,
                rp.role_id,
                r.name AS role_name,
                rp.can_get,
                rp.can_post,
                rp.can_put,
                rp.can_delete
            FROM app.route_permissions rp
            JOIN app.roles r ON r.id = rp.role_id
            WHERE rp.route_id = %s
            ORDER BY r.name
        """, [route_id])
        return _dictfetchall(cursor)


def get_permissions_by_role(role_id):
    """Obtiene todas las rutas a las que tiene acceso un rol."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                rp.id,
                rp.role_id,
                r.name AS role_name,
                rp.route_id,
                vr.url_path,
                vr.name AS route_name,
                rp.can_get,
                rp.can_post,
                rp.can_put,
                rp.can_delete
            FROM app.route_permissions rp
            JOIN app.roles r ON r.id = rp.role_id
            JOIN app.view_routes vr ON vr.id = rp.route_id
            WHERE rp.role_id = %s
            ORDER BY vr.url_path
        """, [role_id])
        return _dictfetchall(cursor)


def get_permissions_by_user(user_id):
    """
    Obtiene las rutas accesibles para un usuario, a través de sus roles.
    Si un usuario tiene varios roles, se combinan los permisos (OR lógico).
    Incluye datos de jerarquía (módulo, familia, subfamilia).
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                rp.route_id,
                vr.url_path,
                vr.name AS route_name,
                BOOL_OR(rp.can_get) AS can_get,
                BOOL_OR(rp.can_post) AS can_post,
                BOOL_OR(rp.can_put) AS can_put,
                BOOL_OR(rp.can_delete) AS can_delete,
                vr.module_id,
                m.name AS module_name,
                m.icon AS module_icon,
                m.display_order AS module_order,
                vr.family_id,
                f.name AS family_name,
                f.icon AS family_icon,
                f.display_order AS family_order,
                vr.subfamily_id,
                sf.name AS subfamily_name,
                sf.icon AS subfamily_icon,
                sf.display_order AS subfamily_order
            FROM app.route_permissions rp
            JOIN app.view_routes vr ON vr.id = rp.route_id
            JOIN app.user_roles ur ON ur.role_id = rp.role_id
            LEFT JOIN app.modules m ON m.id = vr.module_id
            LEFT JOIN app.families f ON f.id = vr.family_id
            LEFT JOIN app.subfamilies sf ON sf.id = vr.subfamily_id
            WHERE ur.user_id = %s
              AND vr.is_active = TRUE
            GROUP BY rp.route_id, vr.url_path, vr.name,
                     vr.module_id, m.name, m.icon, m.display_order,
                     vr.family_id, f.name, f.icon, f.display_order,
                     vr.subfamily_id, sf.name, sf.icon, sf.display_order
            ORDER BY m.display_order NULLS LAST, f.display_order NULLS LAST, sf.display_order NULLS LAST, vr.url_path
        """, [user_id])
        return _dictfetchall(cursor)


def create_permission(data):
    """Asigna permisos a un rol para una ruta."""
    role_id = data["role_id"]
    route_id = data["route_id"]

    with connection.cursor() as cursor:
        # Verificar si ya existe
        cursor.execute("""
            SELECT 1 FROM app.route_permissions
            WHERE role_id = %s AND route_id = %s
        """, [role_id, route_id])

        if cursor.fetchone():
            raise ValueError("Este rol ya tiene permisos configurados para esta ruta")

        cursor.execute("""
            INSERT INTO app.route_permissions (role_id, route_id, can_get, can_post, can_put, can_delete, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, [
            role_id,
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
    Verifica si un usuario tiene permiso para un método HTTP en una ruta,
    a través de cualquiera de sus roles.
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
            SELECT BOOL_OR(rp.{method_col})
            FROM app.route_permissions rp
            JOIN app.view_routes vr ON vr.id = rp.route_id
            JOIN app.user_roles ur ON ur.role_id = rp.role_id
            WHERE ur.user_id = %s
              AND vr.url_path = %s
              AND vr.is_active = TRUE
        """, [user_id, url_path])
        row = cursor.fetchone()
        return bool(row and row[0])


# Mapeo de prefijo API → nombre de ruta vista
API_TO_VIEW_MAP = {
    '/api/routes/': 'view-routes',
    '/api/permissions/': 'route-permissions',
    '/api/users/': 'view-users',
    '/api/roles/': 'view-roles',
    '/api/user-roles/': 'view-user-roles',
    '/api/modules/': 'view-modules',
    '/api/families/': 'view-families',
    '/api/subfamilies/': 'view-subfamilies',
    '/api/recordings/': 'view-spectrogram',
    '/api/shazam/': 'view-shazam',
}


def check_api_permission(role_ids, api_path, perm_field):
    """
    Verifica si alguno de los role_ids tiene el permiso (perm_field)
    para la API solicitada, mapeando la API a su view_route correspondiente.
    
    role_ids: lista de int [1, 2, ...]
    api_path: str, ej: '/api/routes/create/'
    perm_field: str, ej: 'can_get', 'can_post', 'can_put', 'can_delete'
    
    Retorna True si tiene permiso, False si no.
    """
    if not role_ids:
        return False

    # Encontrar a qué vista corresponde esta API
    view_name = None
    for prefix, name in API_TO_VIEW_MAP.items():
        if api_path.startswith(prefix):
            view_name = name
            break

    if not view_name:
        # Si no está en el mapa, permitir acceso (API no controlada)
        return True

    # Validar que perm_field sea seguro (evitar SQL injection)
    if perm_field not in ('can_get', 'can_post', 'can_put', 'can_delete'):
        return False

    placeholders = ','.join(['%s'] * len(role_ids))

    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT BOOL_OR(rp.{perm_field})
            FROM app.route_permissions rp
            JOIN app.view_routes vr ON vr.id = rp.route_id
            WHERE rp.role_id IN ({placeholders})
              AND vr.name = %s
              AND vr.is_active = TRUE
        """, [*role_ids, view_name])
        row = cursor.fetchone()
        return bool(row and row[0])
