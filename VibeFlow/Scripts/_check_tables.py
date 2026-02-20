import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VibeFlow.settings')
import django
django.setup()
from django.db import connection

cursor = connection.cursor()

# 1. Crear módulo "Usuarios"
cursor.execute("""
    INSERT INTO app.modules (name, icon, display_order, is_active, created_at, updated_at)
    VALUES ('Usuarios', '👥', 3, TRUE, NOW(), NOW())
    ON CONFLICT (name) DO UPDATE SET name='Usuarios'
    RETURNING id
""")
mod_id = cursor.fetchone()[0]
print(f"Módulo 'Usuarios' id={mod_id}")

# 2. Crear familias: Usuarios y Roles
for fam_name, fam_icon, fam_order in [('Usuarios', '👤', 1), ('Roles', '🛡️', 2)]:
    cursor.execute("""
        INSERT INTO app.families (module_id, name, icon, display_order, is_active, created_at, updated_at)
        VALUES (%s, %s, %s, %s, TRUE, NOW(), NOW())
        ON CONFLICT (module_id, name) DO UPDATE SET name=EXCLUDED.name
        RETURNING id
    """, [mod_id, fam_name, fam_icon, fam_order])
    fam_id = cursor.fetchone()[0]
    print(f"  Familia '{fam_name}' id={fam_id}")

    # 3. Crear subfamilias: Archivos, Procesos, Consultas
    for sf_name, sf_icon, sf_order in [('Archivos', '📁', 1), ('Procesos', '⚙️', 2), ('Consultas', '🔍', 3)]:
        cursor.execute("""
            INSERT INTO app.subfamilies (family_id, name, icon, display_order, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, TRUE, NOW(), NOW())
            ON CONFLICT (family_id, name) DO UPDATE SET name=EXCLUDED.name
            RETURNING id
        """, [fam_id, sf_name, sf_icon, sf_order])
        sf_id = cursor.fetchone()[0]
        print(f"    Subfamilia '{sf_name}' id={sf_id}")

# 4. Asignar rutas
# view-users → Usuarios / Usuarios / Procesos
cursor.execute("SELECT id FROM app.families WHERE module_id=%s AND name='Usuarios'", [mod_id])
fam_usuarios = cursor.fetchone()[0]
cursor.execute("SELECT id FROM app.subfamilies WHERE family_id=%s AND name='Procesos'", [fam_usuarios])
sf_usuarios_proc = cursor.fetchone()[0]

cursor.execute("""
    UPDATE app.view_routes SET module_id=%s, family_id=%s, subfamily_id=%s, updated_at=NOW()
    WHERE name='view-users'
""", [mod_id, fam_usuarios, sf_usuarios_proc])
print(f"\nRuta 'view-users' → Usuarios / Usuarios / Procesos")

# view-roles → Usuarios / Roles / Procesos
cursor.execute("SELECT id FROM app.families WHERE module_id=%s AND name='Roles'", [mod_id])
fam_roles = cursor.fetchone()[0]
cursor.execute("SELECT id FROM app.subfamilies WHERE family_id=%s AND name='Procesos'", [fam_roles])
sf_roles_proc = cursor.fetchone()[0]

cursor.execute("""
    UPDATE app.view_routes SET module_id=%s, family_id=%s, subfamily_id=%s, updated_at=NOW()
    WHERE name='view-roles'
""", [mod_id, fam_roles, sf_roles_proc])
print(f"Ruta 'view-roles' → Usuarios / Roles / Procesos")

# view-user-roles → Usuarios / Roles / Procesos (asignación de roles a usuarios)
cursor.execute("""
    UPDATE app.view_routes SET module_id=%s, family_id=%s, subfamily_id=%s, updated_at=NOW()
    WHERE name='view-user-roles'
""", [mod_id, fam_roles, sf_roles_proc])
print(f"Ruta 'view-user-roles' → Usuarios / Roles / Procesos")

print("\n✅ Estructura creada exitosamente")
