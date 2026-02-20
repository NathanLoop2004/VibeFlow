"""
jwtService.py - Servicio de generación y validación de JWT.
Usa PyJWT con el SECRET_KEY de Django.
"""

import jwt
import datetime
from django.conf import settings

# Duración del token por tipo de rol
TOKEN_EXPIRY_ADMIN_HOURS = 1
TOKEN_EXPIRY_USER_HOURS = 24
ALGORITHM = 'HS256'


def generate_token(user_data, roles=None):
    """
    Genera un JWT con los datos del usuario y sus roles.
    Admin: expira en 1 hora. Usuario normal: 24 horas.
    """
    role_names = [r['role_name'] for r in (roles or [])]
    role_ids = [r['role_id'] for r in (roles or [])]

    is_admin = 'admin' in role_names
    expiry_hours = TOKEN_EXPIRY_ADMIN_HOURS if is_admin else TOKEN_EXPIRY_USER_HOURS

    payload = {
        'user_id': user_data['id'],
        'username': user_data['username'],
        'email': user_data.get('email', ''),
        'roles': role_names,
        'role_ids': role_ids,
        'iat': datetime.datetime.now(datetime.timezone.utc),
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=expiry_hours),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token):
    """
    Verifica y decodifica un JWT.
    Retorna el payload (dict) si es válido, None si expiró o es inválido.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
