"""
0009_drop_public_duplicates.py - Eliminar tablas duplicadas del schema public.

Django está configurado con search_path=app, así que las tablas del schema
'public' son restos de la configuración inicial y están duplicadas.
Sus índices se reportan como duplicados en el linter de Supabase.

Esta migración:
  1. Elimina todas las tablas sobrantes del schema 'public'.
  2. Elimina el índice duplicado 'idx_fingerprint_hash' en app.fingerprints
     (ya existe 'fingerprints_hash_9cee0884' en la misma columna).
"""

from django.db import migrations


# Tablas que existen en public y son duplicadas de app
PUBLIC_TABLES = [
    'django_admin_log',
    'auth_user_user_permissions',
    'auth_user_groups',
    'auth_group_permissions',
    'user_roles',
    'route_permissions',
    'recordings',
    'django_session',
    'auth_permission',
    'users',
    'roles',
    'auth_user',
    'auth_group',
    'django_content_type',
    # NO incluir django_migrations: Django lo necesita para registrar migraciones
]


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_enable_rls_public'),
    ]

    operations = [
        # 1. Eliminar tablas duplicadas del schema public
        #    CASCADE elimina también las constraints/FK dependientes
        migrations.RunSQL(
            sql=';\n'.join(
                f'DROP TABLE IF EXISTS public."{t}" CASCADE'
                for t in PUBLIC_TABLES
            ) + ';',
            reverse_sql=migrations.RunSQL.noop,
        ),

        # 2. Eliminar índice duplicado en app.fingerprints
        #    Django ya creó 'fingerprints_hash_9cee0884' via db_index=True
        #    e 'idx_fingerprint_hash' via Meta.indexes → son redundantes
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS app.idx_fingerprint_hash;',
            reverse_sql='CREATE INDEX idx_fingerprint_hash ON app.fingerprints (hash);',
        ),
    ]
