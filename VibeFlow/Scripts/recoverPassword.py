"""
Script para recuperar/restablecer la contraseña de la base de datos de Supabase.

Uso:
    python recoverPassword.py

Requisitos:
    - pip install requests
    - Token de acceso de Supabase (se obtiene en https://app.supabase.com/account/tokens)
    - Project Reference ID (se obtiene en Settings > General en el dashboard de Supabase)
"""

import requests
import sys
import string
import secrets


SUPABASE_MANAGEMENT_API = "https://api.supabase.com/v1"


def generate_secure_password(length: int = 24) -> str:
    """Genera una contraseña segura aleatoria."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Verificar que tenga al menos una mayúscula, una minúscula, un dígito y un símbolo
        if (any(c.isupper() for c in password)
                and any(c.islower() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*" for c in password)):
            return password


def get_project_info(access_token: str, project_ref: str) -> dict | None:
    """Obtiene información del proyecto de Supabase."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"{SUPABASE_MANAGEMENT_API}/projects/{project_ref}",
        headers=headers,
    )
    if response.status_code == 200:
        return response.json()
    return None


def reset_database_password(access_token: str, project_ref: str, new_password: str) -> bool:
    """
    Restablece la contraseña de la base de datos de Supabase usando la Management API.

    Args:
        access_token: Token de acceso personal de Supabase.
        project_ref: ID de referencia del proyecto.
        new_password: Nueva contraseña para la base de datos.

    Returns:
        True si se restableció correctamente, False en caso contrario.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {"password": new_password}

    response = requests.patch(
        f"{SUPABASE_MANAGEMENT_API}/projects/{project_ref}/database/password",
        headers=headers,
        json=payload,
    )

    if response.status_code in (200, 201):
        return True
    else:
        print(f"[ERROR] Código de estado: {response.status_code}")
        print(f"[ERROR] Respuesta: {response.text}")
        return False


def get_connection_string(project_ref: str, new_password: str) -> str:
    """Genera el string de conexión PostgreSQL actualizado."""
    return (
        f"postgresql://postgres.{project_ref}:{new_password}"
        f"@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    )


def main():
    print("=" * 60)
    print("  Recuperación de contraseña - Supabase Database")
    print("=" * 60)
    print()

    # Solicitar credenciales
    access_token = input(
        "Ingresa tu Access Token de Supabase\n"
        "(Obténlo en https://app.supabase.com/account/tokens): "
    ).strip()

    if not access_token:
        print("[ERROR] El Access Token es obligatorio.")
        sys.exit(1)

    project_ref = input(
        "\nIngresa el Project Reference ID\n"
        "(Encuéntralo en Settings > General en el dashboard): "
    ).strip()

    if not project_ref:
        print("[ERROR] El Project Reference ID es obligatorio.")
        sys.exit(1)

    # Verificar proyecto
    print("\nVerificando proyecto...")
    project_info = get_project_info(access_token, project_ref)
    if project_info:
        print(f"Proyecto encontrado: {project_info.get('name', 'N/A')}")
        print(f"Región: {project_info.get('region', 'N/A')}")
        print(f"Estado: {project_info.get('status', 'N/A')}")
    else:
        print("[AVISO] No se pudo verificar el proyecto. Verifica tu token y project ref.")
        continuar = input("¿Deseas continuar de todos modos? (s/n): ").strip().lower()
        if continuar != 's':
            sys.exit(0)

    # Opción de contraseña
    print("\n¿Cómo deseas establecer la nueva contraseña?")
    print("  1. Generar una contraseña segura automáticamente")
    print("  2. Ingresar una contraseña manualmente")

    opcion = input("\nElige una opción (1/2): ").strip()

    if opcion == "1":
        new_password = generate_secure_password()
        print(f"\nContraseña generada: {new_password}")
    elif opcion == "2":
        new_password = input("\nIngresa la nueva contraseña (mínimo 12 caracteres): ").strip()
        if len(new_password) < 12:
            print("[ERROR] La contraseña debe tener al menos 12 caracteres.")
            sys.exit(1)
    else:
        print("[ERROR] Opción no válida.")
        sys.exit(1)

    # Confirmar
    print("\n" + "-" * 60)
    print("Resumen:")
    print(f"  Proyecto: {project_ref}")
    print(f"  Nueva contraseña: {new_password}")
    print("-" * 60)

    confirmar = input("\n¿Confirmas el cambio de contraseña? (s/n): ").strip().lower()
    if confirmar != 's':
        print("Operación cancelada.")
        sys.exit(0)

    # Ejecutar cambio
    print("\nRestableciendo contraseña...")
    success = reset_database_password(access_token, project_ref, new_password)

    if success:
        print("\n[OK] Contraseña restablecida exitosamente.")
        print("\n" + "=" * 60)
        print("  INFORMACIÓN DE CONEXIÓN ACTUALIZADA")
        print("=" * 60)

        conn_string = get_connection_string(project_ref, new_password)
        print(f"\nConnection String:\n  {conn_string}")

        print(f"\nPara tu settings.py de Django:")
        print(f"""
DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.{project_ref}',
        'PASSWORD': '{new_password}',
        'HOST': 'aws-0-us-east-1.pooler.supabase.com',
        'PORT': '6543',
    }}
}}
""")
        print("[!] GUARDA esta contraseña en un lugar seguro.")
        print("[!] Actualiza tu settings.py o variables de entorno con la nueva contraseña.")
    else:
        print("\n[ERROR] No se pudo restablecer la contraseña.")
        print("Verifica:")
        print("  - Que el Access Token sea válido y tenga permisos suficientes")
        print("  - Que el Project Reference ID sea correcto")
        print("  - Tu conexión a internet")


if __name__ == "__main__":
    main()