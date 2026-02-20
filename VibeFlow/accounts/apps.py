from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'VibeFlow.accounts'
    label = 'accounts'  # Mantener label original para migrar sin problemas

    def ready(self):
        from django.db.backends.signals import connection_created

        def set_search_path(sender, connection, **kwargs):
            """Fuerza search_path=app en cada conexión nueva.
            El pooler de Supabase (PgBouncer transaction-mode) puede
            ignorar '-c search_path=app' del connection string."""
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO app;")

        connection_created.connect(set_search_path)
