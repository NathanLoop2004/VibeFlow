"""
googleAuthService.py - Servicio para verificar tokens de Google OAuth.
Usa el endpoint tokeninfo de Google para validar el credential.
"""

import os
import requests as http_requests

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')

GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')


def verify_google_token(credential):
    """
    Verifica el token de Google (credential) usando el endpoint tokeninfo.
    Retorna un dict con la info del usuario de Google si es válido, None si no.
    """
    client_id = GOOGLE_CLIENT_ID
    if not client_id:
        print("[Google Auth] ERROR: GOOGLE_CLIENT_ID no configurado")
        return None

    try:
        # Verificar el id_token con Google directamente
        resp = http_requests.get(
            'https://oauth2.googleapis.com/tokeninfo',
            params={'id_token': credential},
            timeout=10,
        )

        print(f"[Google Auth] tokeninfo status: {resp.status_code}")

        if resp.status_code != 200:
            print(f"[Google Auth] tokeninfo error: {resp.text}")
            return None

        idinfo = resp.json()

        # Verificar que el audience coincida con nuestro client_id
        if idinfo.get('aud') != client_id:
            print(f"[Google Auth] AUD mismatch: {idinfo.get('aud')} != {client_id}")
            return None

        email = idinfo.get('email', '')
        print(f"[Google Auth] Verificado OK - email: {email}")

        return {
            'google_id': idinfo.get('sub', ''),
            'email': email,
            'name': idinfo.get('name', email.split('@')[0]),
            'picture': idinfo.get('picture', ''),
            'email_verified': idinfo.get('email_verified', 'false') == 'true',
        }
    except Exception as e:
        print(f"[Google Auth] Error: {e}")
        return None


def verify_access_token(access_token):
    """
    Verifica un access_token de Google usando el endpoint userinfo.
    Se usa cuando FedCM no está disponible y el frontend envía un access_token
    en vez de un id_token (credential).
    """
    try:
        resp = http_requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10,
        )

        print(f"[Google Auth] userinfo status: {resp.status_code}")

        if resp.status_code != 200:
            print(f"[Google Auth] userinfo error: {resp.text}")
            return None

        info = resp.json()
        email = info.get('email', '')
        print(f"[Google Auth] access_token verificado OK - email: {email}")

        return {
            'google_id': info.get('sub', ''),
            'email': email,
            'name': info.get('name', email.split('@')[0]),
            'picture': info.get('picture', ''),
            'email_verified': info.get('email_verified', False),
        }
    except Exception as e:
        print(f"[Google Auth] Error verify_access_token: {e}")
        return None


def exchange_code_for_user(code, redirect_uri):
    """
    Intercambia un authorization code de Google por un access_token,
    luego obtiene la info del usuario con el access_token.
    Flujo OAuth2 estándar sin librería GSI.
    """
    client_id = GOOGLE_CLIENT_ID
    client_secret = GOOGLE_CLIENT_SECRET

    if not client_secret:
        print("[Google Auth] ERROR: GOOGLE_CLIENT_SECRET no configurado")
        return None

    try:
        # 1. Intercambiar code por tokens
        token_resp = http_requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code',
            },
            timeout=10,
        )

        print(f"[Google Auth] token exchange status: {token_resp.status_code}")

        if token_resp.status_code != 200:
            print(f"[Google Auth] token exchange error: {token_resp.text}")
            return None

        tokens = token_resp.json()
        access_token = tokens.get('access_token', '')

        if not access_token:
            print("[Google Auth] No se recibió access_token en el intercambio")
            return None

        # 2. Obtener info del usuario con el access_token
        return verify_access_token(access_token)

    except Exception as e:
        print(f"[Google Auth] Error exchange_code_for_user: {e}")
        return None
