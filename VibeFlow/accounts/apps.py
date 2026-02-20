from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'VibeFlow.accounts'
    label = 'accounts'  # Mantener label original para migrar sin problemas
