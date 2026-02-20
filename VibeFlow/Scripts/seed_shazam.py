"""Inserta view_route y route_permission para Shazam."""
from django.db import connection

with connection.cursor() as c:
    c.execute("""
        INSERT INTO app.view_routes
            (url_path, template_name, name, is_active, module_id, family_id, subfamily_id, created_at, updated_at)
        VALUES
            ('views/shazam', 'Shazam/shazam.html', 'view-shazam', TRUE, 4, 9, NULL, NOW(), NOW())
        RETURNING id
    """)
    route_id = c.fetchone()[0]
    print(f"view_route created with id={route_id}")

    c.execute("""
        INSERT INTO app.route_permissions
            (role_id, route_id, can_get, can_post, can_put, can_delete, created_at, updated_at)
        VALUES
            (1, %s, TRUE, TRUE, TRUE, TRUE, NOW(), NOW())
        RETURNING id
    """, [route_id])
    perm_id = c.fetchone()[0]
    print(f"route_permission created with id={perm_id}")

print("Done!")
