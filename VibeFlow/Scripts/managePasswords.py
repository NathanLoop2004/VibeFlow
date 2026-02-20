"""
Script para gestionar contraseñas de usuarios en VibeFlow.

Opciones:
  1. Probar una contraseña contra el hash de un usuario
  2. Resetear la contraseña de un usuario

Uso:
    python VibeFlow/Scripts/managePasswords.py

No se puede "desencriptar" bcrypt — es un hash de una sola vía.
Solo se puede verificar si una contraseña coincide con el hash.
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VibeFlow.settings')
django.setup()

import bcrypt as _bcrypt
from django.db import connection


def get_all_users():
    """Obtiene todos los usuarios con su hash."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, username, email, password_hash
            FROM app.users
            ORDER BY created_at DESC
        """)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def verify_password(password, hashed):
    """Verifica si una contraseña coincide con el hash."""
    return _bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def reset_password(user_id, new_password):
    """Resetea la contraseña de un usuario."""
    new_hash = _bcrypt.hashpw(new_password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE app.users
            SET password_hash = %s, updated_at = NOW()
            WHERE id = %s
        """, [new_hash, user_id])
        return cursor.rowcount > 0


def main():
    print("\n" + "=" * 50)
    print("  🔑 VibeFlow - Gestión de Contraseñas")
    print("=" * 50)

    users = get_all_users()

    if not users:
        print("\n❌ No hay usuarios en la base de datos.")
        return

    # Mostrar usuarios
    print("\n📋 Usuarios registrados:\n")
    for i, u in enumerate(users, 1):
        print(f"  {i}. {u['username']} ({u['email']})")

    # Elegir acción
    print("\n¿Qué deseas hacer?")
    print("  1. Probar una contraseña")
    print("  2. Resetear contraseña")
    print("  3. Salir")

    opcion = input("\nOpción: ").strip()

    if opcion == '1':
        # --- Probar contraseña ---
        num = input("Número de usuario: ").strip()
        try:
            user = users[int(num) - 1]
        except (ValueError, IndexError):
            print("❌ Número inválido")
            return

        password = input(f"Contraseña a probar para '{user['username']}': ").strip()

        if verify_password(password, user['password_hash']):
            print(f"\n✅ ¡Correcto! La contraseña de '{user['username']}' es: {password}")
        else:
            print(f"\n❌ La contraseña NO coincide para '{user['username']}'")

    elif opcion == '2':
        # --- Resetear contraseña ---
        num = input("Número de usuario: ").strip()
        try:
            user = users[int(num) - 1]
        except (ValueError, IndexError):
            print("❌ Número inválido")
            return

        new_pass = input(f"Nueva contraseña para '{user['username']}': ").strip()
        if not new_pass:
            print("❌ La contraseña no puede estar vacía")
            return

        confirm = input(f"¿Confirmas resetear la contraseña de '{user['username']}'? (s/n): ").strip().lower()
        if confirm != 's':
            print("Cancelado.")
            return

        if reset_password(user['id'], new_pass):
            print(f"\n✅ Contraseña de '{user['username']}' actualizada correctamente.")
            print(f"   Nueva contraseña: {new_pass}")
        else:
            print("❌ Error al actualizar la contraseña")

    elif opcion == '3':
        print("👋 Adiós!")
    else:
        print("❌ Opción no válida")


if __name__ == '__main__':
    main()
