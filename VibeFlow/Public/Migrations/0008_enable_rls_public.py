"""
0008_enable_rls_public.py - Habilitar Row Level Security en tablas public.

Supabase expone el schema 'public' via PostgREST (API REST anónima).
Sin RLS cualquier persona con la URL del proyecto podría leer/escribir
las tablas Django directamente saltándose la app.

Esta migración:
  1. Activa RLS en cada tabla del schema public.
  2. Crea una policy que permite acceso total al rol 'postgres'
     (el que usa Django a través del connection pooler de Supabase).
  3. Bloquea el acceso vía los roles anon/authenticated de PostgREST.
"""

from django.db import migrations

# Todas las tablas del schema public que reporta el linter
TABLES = [
    'recordings',
    'roles',
    'users',
    'user_roles',
    'route_permissions',
    'django_migrations',
    'django_content_type',
    'django_admin_log',
    'django_session',
    'auth_permission',
    'auth_group',
    'auth_group_permissions',
    'auth_user',
    'auth_user_groups',
    'auth_user_user_permissions',
]


def build_forward_sql():
    """Genera el SQL para activar RLS y crear las policies."""
    statements = []
    for table in TABLES:
        statements.append(
            f'ALTER TABLE public."{table}" ENABLE ROW LEVEL SECURITY;'
        )
        # Policy: solo el rol postgres (Django) tiene acceso completo
        statements.append(
            f'CREATE POLICY "django_full_access" ON public."{table}" '
            f'FOR ALL TO postgres USING (true) WITH CHECK (true);'
        )
    return '\n'.join(statements)


def build_reverse_sql():
    """Genera el SQL para revertir: eliminar policies y desactivar RLS."""
    statements = []
    for table in TABLES:
        statements.append(
            f'DROP POLICY IF EXISTS "django_full_access" ON public."{table}";'
        )
        statements.append(
            f'ALTER TABLE public."{table}" DISABLE ROW LEVEL SECURITY;'
        )
    return '\n'.join(statements)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_songs_terabox'),
    ]

    operations = [
        migrations.RunSQL(
            sql=build_forward_sql(),
            reverse_sql=build_reverse_sql(),
        ),
    ]
