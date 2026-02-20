"""
run_servers.py - Inicia ambos servidores: HTTP (8000) y HTTPS (8443)
Uso: python VibeFlow/Scripts/run_servers.py
"""

import subprocess
import sys
import os
import time

# BASE_DIR = raíz del proyecto (donde está manage.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))

# Cargar .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, '.env'))
except ImportError:
    pass


def main():
    print("=" * 50)
    print("  VibeFlow - Servidores HTTP & HTTPS")
    print("=" * 50)
    print()
    print("  HTTP  -> http://localhost:8000")
    print("  HTTPS -> https://localhost:8443")
    print()
    print("  Presiona Ctrl+C para detener ambos")
    print("=" * 50)

    # Leer rutas de certificados desde .env (o usar default)
    cert_file = os.path.join(
        BASE_DIR,
        os.getenv('SSL_CERTFILE', 'VibeFlow/certs/localhost.crt'),
    )
    key_file = os.path.join(
        BASE_DIR,
        os.getenv('SSL_KEYFILE', 'VibeFlow/certs/localhost.key'),
    )

    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print(f"\n[ERROR] No se encontraron certificados SSL:")
        print(f"  cert: {cert_file}")
        print(f"  key:  {key_file}")
        print("Verifica SSL_CERTFILE y SSL_KEYFILE en tu .env")
        sys.exit(1)

    processes = []

    try:
        # Servidor HTTP en puerto 8000 (Django runserver)
        http_proc = subprocess.Popen(
            [sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'],
            cwd=BASE_DIR,
        )
        processes.append(http_proc)
        print("\n[OK] Servidor HTTP iniciado en puerto 8000")

        time.sleep(1)

        # Servidor HTTPS en puerto 8443 (uvicorn con SSL)
        https_proc = subprocess.Popen(
            [
                sys.executable, '-m', 'uvicorn',
                'VibeFlow.asgi:application',
                '--host', '0.0.0.0',
                '--port', '8443',
                '--ssl-certfile', cert_file,
                '--ssl-keyfile', key_file,
                '--reload',
            ],
            cwd=BASE_DIR,
        )
        processes.append(https_proc)
        print("[OK] Servidor HTTPS iniciado en puerto 8443\n")

        # Esperar a que terminen
        for proc in processes:
            proc.wait()

    except KeyboardInterrupt:
        print("\n\nDeteniendo servidores...")
        for proc in processes:
            proc.terminate()
        for proc in processes:
            proc.wait()
        print("Servidores detenidos.")


if __name__ == '__main__':
    main()
