"""
Herramienta local para gestionar contraseñas con bcrypt.
No requiere conexión a Supabase ni Django.

Uso:
    python VibeFlow/Scripts/passwordTool.py

Opciones:
  1. Generar hash bcrypt a partir de una contraseña
  2. Verificar si una contraseña coincide con un hash
  3. Generar contraseña segura aleatoria
"""

import bcrypt
import string
import secrets


def generate_hash(password: str) -> str:
    """Genera un hash bcrypt a partir de una contraseña en texto plano."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verifica si una contraseña coincide con un hash bcrypt."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        print(f"  Error al verificar: {e}")
        return False


def generate_secure_password(length: int = 16) -> str:
    """Genera una contraseña segura aleatoria."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*_-"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.isupper() for c in password)
                and any(c.islower() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*_-" for c in password)):
            return password


def main():
    while True:
        print("\n" + "=" * 50)
        print("  Herramienta de Contraseñas (bcrypt)")
        print("=" * 50)
        print("\n  1. Generar hash desde una contraseña")
        print("  2. Verificar contraseña contra un hash")
        print("  3. Generar contraseña segura aleatoria")
        print("  4. Salir")

        opcion = input("\nOpcion: ").strip()

        if opcion == '1':
            password = input("Contraseña: ").strip()
            if not password:
                print("  La contraseña no puede estar vacia")
                continue
            hashed = generate_hash(password)
            print(f"\n  Hash generado:")
            print(f"  {hashed}")
            print(f"\n  Puedes usar este hash para INSERT/UPDATE en la DB:")
            print(f"  UPDATE app.users SET password_hash = '{hashed}' WHERE username = 'TU_USUARIO';")

        elif opcion == '2':
            password = input("Contraseña a probar: ").strip()
            hashed = input("Hash bcrypt (empieza con $2b$): ").strip()
            if not password or not hashed:
                print("  Ambos campos son requeridos")
                continue
            if verify_password(password, hashed):
                print(f"\n  CORRECTO - La contraseña coincide con el hash")
            else:
                print(f"\n  INCORRECTO - La contraseña NO coincide")

        elif opcion == '3':
            try:
                length = input("Longitud (default 16): ").strip()
                length = int(length) if length else 16
            except ValueError:
                length = 16
            password = generate_secure_password(length)
            hashed = generate_hash(password)
            print(f"\n  Contraseña generada: {password}")
            print(f"  Hash bcrypt:         {hashed}")

        elif opcion == '4':
            print("Adios!")
            break
        else:
            print("  Opcion no valida")


if __name__ == '__main__':
    main()
