"""
googleAuthService.py - Servicio para verificar tokens de Google OAuth.
Usa el endpoint tokeninfo de Google para validar el credential.
"""

import os
import requests as http_requests

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')


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
