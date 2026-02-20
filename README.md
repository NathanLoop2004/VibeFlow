<p align="center">
  <img src="https://img.shields.io/badge/Django-6.0.2-092E20?logo=django" />
  <img src="https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-Supabase-4169E1?logo=supabase&logoColor=white" />
  <img src="https://img.shields.io/badge/Channels-4.3.2-FF6600?logo=django" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

# 🎵 VibeFlow

**Panel de administración inteligente con identificación de audio en tiempo real.**

VibeFlow combina un sistema completo de gestión de usuarios, roles y permisos con un motor de fingerprinting de audio tipo Shazam, streaming por WebSocket y almacenamiento en la nube.

---

## ✨ Características Principales

| Feature | Descripción |
|---------|-------------|
| 🔐 **Auth JWT + Google OAuth** | Login con tokens seguros (HS256) y Google Sign-In en un clic |
| 👥 **Gestión de Usuarios y Roles** | CRUD completo con asignación de roles y permisos granulares |
| 🗺️ **Rutas Dinámicas** | Vistas registradas en BD con permisos GET/POST/PUT/DELETE por rol |
| 📦 **Módulos → Familias → Subfamilias** | Navegación jerárquica de 3 niveles |
| 🎙️ **Shazam (Audio Fingerprinting)** | Identificación de canciones por constelación espectral |
| ⚡ **WebSocket Streaming** | Envío de audio en tiempo real con respuestas parciales/confirmadas |
| ☁️ **TeraBox (1TB gratis)** | Audio almacenado en la nube; solo hashes en la BD |
| 🔒 **Row Level Security** | RLS habilitado en todas las tablas de Supabase |
| 🌐 **HTTP + HTTPS** | Servidor dual con certificado SSL |

---

## 🏗️ Arquitectura

```
VibeFlow/
├── manage.py
├── .env                          # Variables de entorno
├── VibeFlow/
│   ├── settings.py               # Config Django + Supabase + Channels
│   ├── asgi.py                   # HTTP → Django, WebSocket → Channels
│   ├── urls.py                   # Punto de entrada de rutas
│   │
│   ├── accounts/
│   │   └── apps.py               # Signal search_path para Supabase pooler
│   │
│   ├── certs/                    # Certificados SSL (localhost.crt / .key)
│   │
│   ├── Public/
│   │   ├── Models/               # 11 modelos Django ORM (schema: app)
│   │   ├── Services/             # 14 servicios (lógica de negocio)
│   │   ├── Controllers/          # 11 controladores (request handlers)
│   │   ├── Routes/               # Routers por recurso + WebSocket
│   │   ├── Views/                # 14 carpetas de templates HTML (SSR)
│   │   ├── Middleware/           # JWT + permisos por rol
│   │   ├── Consumers/            # WebSocket consumers (Shazam)
│   │   └── Migrations/           # Migraciones (SQL crudo con schema app.)
│   │
│   └── Scripts/                  # Utilidades: servidores, seeds, passwords
```

**Patrón:** Controller → Service → Model (MVC-like)

---

## 🛠️ Tech Stack

| Capa | Tecnología |
|------|------------|
| **Backend** | Django 6.0.2 · Python 3.14 |
| **WebSocket** | Django Channels 4.3.2 · Daphne 4.2.1 |
| **Base de Datos** | PostgreSQL (Supabase) · Schema `app` · Pooler port 6543 |
| **Audio** | NumPy · SciPy · Constellation Map Algorithm |
| **Almacenamiento** | TeraBox API (1TB gratis) · Cookie auth |
| **Auth** | PyJWT (HS256) · Google OAuth 2.0 |
| **SSL** | Uvicorn + certificados auto-firmados |
| **Sesiones** | Signed Cookies |

---

## 📊 Modelos de Datos

| Modelo | Tabla | Descripción |
|--------|-------|-------------|
| `User` | `users` | Usuarios con UUID, verificación, bloqueo por intentos fallidos |
| `Role` | `roles` | Roles del sistema (Admin, User, etc.) |
| `UserRole` | `user_roles` | Asignación usuario ↔ rol |
| `Module` | `modules` | Nivel 1 del menú lateral |
| `Family` | `families` | Nivel 2 del menú (pertenece a Module) |
| `Subfamily` | `subfamilies` | Nivel 3 del menú (pertenece a Family) |
| `ViewRoute` | `view_routes` | Rutas registradas con template asociado |
| `RoutePermission` | `route_permissions` | Permisos CRUD por rol × ruta |
| `Recording` | `recordings` | Grabaciones de audio del usuario |
| `Song` | `songs` | Canciones con ruta TeraBox y conteo de fingerprints |
| `Fingerprint` | `fingerprints` | Hashes SHA-1 con offset temporal (FK → Song) |

---

## 🔌 API Endpoints

### REST API (`/api/`)

| Ruta | Recurso | Métodos |
|------|---------|---------|
| `/api/auth/` | Autenticación | Login, Logout, Google OAuth |
| `/api/users/` | Usuarios | GET, POST, PUT, DELETE |
| `/api/roles/` | Roles | GET, POST, PUT, DELETE |
| `/api/user-roles/` | Asignación de roles | GET, POST, DELETE |
| `/api/routes/` | Rutas de vista | GET, POST, PUT, DELETE |
| `/api/permissions/` | Permisos de ruta | GET, POST, PUT, DELETE |
| `/api/modules/` | Módulos | GET, POST, PUT, DELETE |
| `/api/families/` | Familias | GET, POST, PUT, DELETE |
| `/api/subfamilies/` | Subfamilias | GET, POST, PUT, DELETE |
| `/api/recordings/` | Grabaciones | GET, POST, PUT, DELETE |
| `/api/shazam/` | Shazam | List, Upload, Search, Audio, Regenerate |

### WebSocket

```
ws://localhost:8000/ws/shazam/
```

| Acción | Descripción |
|--------|-------------|
| Enviar **bytes** | Chunks de audio WAV → se acumulan en buffer |
| `{"action": "search"}` | Fuerza análisis del buffer actual |
| `{"action": "reset"}` | Limpia el buffer |
| `{"action": "stop"}` | Cierra la conexión |

Respuestas: `partial_results` (candidatos) o `confirmed` (≥25 matches coherentes).

---

## 🎵 Shazam: Cómo Funciona

```
Audio WAV → Resample 11025 Hz → STFT (1024 ventana, 512 overlap)
    → Detección de picos en 3 bandas espectrales
    → Pares de constelación (deltas: 9, 11, 13 frames)
    → Hash SHA-1 por triplete (f_peak, f_midlow, distance)
    → Búsqueda en BD por coincidencia temporal coherente
    → Umbral: ≥ 25 matches = canción identificada
```

---

## ⚙️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/NathanLoop2004/VibeFlow.git
cd VibeFlow
```

### 2. Instalar dependencias

```bash
pip install django psycopg2-binary python-dotenv pyjwt numpy scipy requests channels daphne uvicorn
```

### 3. Configurar variables de entorno

Crear un archivo `.env` en la raíz:

```env
# Django
SECRET_KEY=tu-secret-key
DEBUG=True

# Base de datos (Supabase)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres.tu-proyecto
DB_PASSWORD=tu-password
DB_HOST=aws-X-us-east-1.pooler.supabase.com
DB_PORT=6543

# Google OAuth
GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com

# SSL (opcional para HTTPS)
SSL_CERTFILE=VibeFlow/certs/localhost.crt
SSL_KEYFILE=VibeFlow/certs/localhost.key

# TeraBox
TERABOX_NDUS=tu-cookie-ndus
TERABOX_FOLDER=/VibeFlow/songs
```

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. Ejecutar

```bash
# Solo HTTP (desarrollo)
python manage.py runserver 0.0.0.0:8000

# HTTP + HTTPS (recomendado)
python VibeFlow/Scripts/run_servers.py
```

| Protocolo | URL |
|-----------|-----|
| HTTP | `http://localhost:8000` |
| HTTPS | `https://localhost:8443` |
| WebSocket | `ws://localhost:8000/ws/shazam/` |

---

## 🔐 Autenticación y Permisos

### Flujo de Auth
1. **Login** → `/api/auth/login/` con `username` + `password`
2. **JWT** → Token HS256 (Admin: 1h, User: 24h)
3. **Middleware** → Valida `Authorization: Bearer <token>` en cada request
4. **Permisos** → Consulta `route_permissions` para verificar `can_get/post/put/delete` según rol

### Rutas Públicas (sin auth)
- `/` · `/welcome/` · `/register/` · `/api/auth/*` · `/static/*`

### Google OAuth
- Login/Registro automático con cuenta de Google
- Verificación via endpoint `tokeninfo` de Google

---

## 📁 Scripts Útiles

| Script | Descripción |
|--------|-------------|
| `Scripts/run_servers.py` | Lanza HTTP (8000) + HTTPS (8443) en paralelo |
| `Scripts/managePasswords.py` | Gestión de contraseñas |
| `Scripts/recoverPassword.py` | Recuperación de contraseña |
| `Scripts/seed_shazam.py` | Seed de datos para Shazam |
| `Scripts/seed_shazam_perm.py` | Seed de permisos para Shazam |

---

## 📝 Notas Técnicas

- **Supabase Pooler (PgBouncer):** El `search_path=app` se fuerza via signal `connection_created` en cada conexión nueva, ya que el pooler en modo transacción puede ignorar el parámetro del connection string.
- **Migraciones:** Usar siempre prefijo `app.` en SQL crudo. Para cambios de schema, usar `SeparateDatabaseAndState` para mantener sincronizado el estado interno de Django.
- **RLS:** Habilitado en todas las tablas con política `django_full_access` para el usuario `postgres`.
- **TeraBox:** Requiere cookie `ndus` válida. Flujo de upload: precreate → upload → create.

---

## 📄 Licencia

MIT © 2026 VibeFlow
