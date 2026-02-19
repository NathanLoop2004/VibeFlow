import uuid
from django.db import models


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Información básica
    username = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=150, unique=True)
    password_hash = models.TextField()

    # Estado de la cuenta
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Seguridad
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)

    # Recuperación de contraseña
    reset_token = models.TextField(null=True, blank=True)
    reset_token_expires = models.DateTimeField(null=True, blank=True)

    # Verificación de email
    verification_token = models.TextField(null=True, blank=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        app_label = 'accounts'

    def __str__(self):
        return self.username
