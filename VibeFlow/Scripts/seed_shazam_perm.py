from django.db import connection
c = connection.cursor()
c.execute("INSERT INTO app.route_permissions (role_id, route_id, can_get, can_post, can_put, can_delete, created_at, updated_at) VALUES (1, 13, TRUE, TRUE, TRUE, TRUE, NOW(), NOW()) RETURNING id")
r = c.fetchone()
print(f"perm id={r[0]}")
c.close()
