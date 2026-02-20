# VibeFlow - Registro de Cambios

## [v1.1.0] - 20 de Febrero de 2026

### 🆕 Novedades

#### WebSocket para Audio Streaming en Tiempo Real
- Implementado **Django Channels 4.3.2** + **Daphne 4.2.1** para soporte WebSocket
- Nuevo archivo `asgi.py` con enrutamiento de protocolos (HTTP ↔ Django, WebSocket ↔ URLRouter)
- Nuevo consumidor `ShazamStreamConsumer` (`VibeFlow/Public/Consumers/shazamConsumer.py`)
  - Recibe chunks de audio WAV en streaming
  - Acumula en buffer y analiza automáticamente cada ~5 segundos
  - Soporta acciones: `search` (fuerza análisis), `reset` (limpia buffer), `stop` (cierra conexión)
  - Envía resultados parciales y confirmados en tiempo real
- Frontend actualizado con WebSocket (`VibeFlow/Public/Views/Shazam/shazam.js`)
  - Nueva función `startListening()` con `ScriptProcessorNode` para captura de audio
  - Nueva función `float32ToWav()` para conversión PCM → WAV
  - Tabla de biblioteca con columna "Audio" (estado de almacenamiento en TeraBox)

#### Almacenamiento en Nube TeraBox (1TB Gratis)
- **Nuevo servicio** `VibeFlow/Public/Services/teraboxService.py`
  - Clase `TeraBoxClient` con autenticación por cookie (ndus)
  - Soporte upload/download/delete de archivos de audio
  - Flujo: precreate → upload → create
- **Modelo actualizado** `songsModel.py`
  - Campo `audio_data` (BinaryField) → reemplazado por `terabox_path` (CharField)
  - Ahora solo se almacenan hashes de fingerprints; audio en TeraBox
- **Servicios impactados**:
  - `songsService.py`: Reescrito para usar TeraBox · Nuevas funciones: `update_terabox_path()`, `get_song_terabox_path()`, `get_song_audio()`
  - `shazamController.py`: `subir_cancion` completo: genera fingerprints → crea canción → sube a TeraBox
  - `fingerprintService.py`: `regenerate_song()` descarga audio desde TeraBox
- **Migración aplicada** `0007_songs_terabox.py`
  - Usa SQL crudo con prefijo `app.` para compatible con search_path de Supabase
  - Elimina `audio_data`, agrega `terabox_path`
- **Configuración** en `.env`:
  - `TERABOX_NDUS`: Cookie de autenticación
  - `TERABOX_FOLDER`: Ruta base (`/VibeFlow/songs`)

#### Seguridad: Row Level Security (RLS) en Supabase
- **Migración aplicada** `0008_enable_rls_public.py`
- Habilitó RLS en 15 tablas del schema `public`:
  - Django core: `django_migrations`, `django_content_type`, `django_admin_log`, `django_session`
  - Auth: `auth_permission`, `auth_group`, `auth_group_permissions`, `auth_user`, `auth_user_groups`, `auth_user_user_permissions`
  - VibeFlow: `recordings`, `roles`, `users`, `user_roles`, `route_permissions`
- Creada política `django_full_access` para usuario `postgres` (permite acceso completo)
- Resuelve errores de seguridad reportados por Supabase

#### Limpieza de Índices Duplicados
- **Problema**: ~40 índices duplicados entre schemas `app` y `public` (por configuración search_path)
- **Solución** Migración `0009_drop_public_duplicates.py`:
  - ✅ Eliminadas 14 tablas duplicadas del schema `public`
  - ✅ Eliminado índice redundante `idx_fingerprint_hash` (ya existía `fingerprints_hash_9cee0884`)
  - ✅ Preservado `public.django_migrations` (requerido por Django)
- **Resultado**: Todas las advertencias de índices duplicados en Supabase se resolvieron
- Base de datos ahora limpia y optimizada

### 📦 Dependencias Instaladas
```
Django==6.0.2
channels==4.3.2
daphne==4.2.1
```

### 🔧 Cambios Técnicos Importantes

| Archivo | Cambio |
|---------|--------|
| `settings.py` | `daphne` + `channels` en INSTALLED_APPS, ASGI_APPLICATION configurado |
| `asgi.py` | Enrutador de protocolos (HTTP/WebSocket) reescrito |
| `Models/songsModel.py` | `audio_data` → `terabox_path` |
| `Services/songsService.py` | Reescrito para TeraBox |
| `.env` | Agregadas `TERABOX_*` vars |

### ✅ Estado Actual
- ✅ WebSocket funcionando para streaming de audio
- ✅ Almacenamiento en TeraBox operativo
- ✅ RLS habilitado en Supabase
- ✅ Base de datos optimizada (sin índices duplicados)
- ✅ Django healthy + todas las migraciones aplicadas

### 📝 Notas para Desarrolladores
1. **WebSocket**: Ruta `ws://localhost:8000/ws/shazam/` lista para cliente
2. **TeraBox**: Requiere cookie `ndus` válida en `.env`
3. **Migrations**: Recuerda siempre usar prefijo `app.` en SQL raw para Supabase
4. **Search Path**: BD usa schema `app` por defecto (`OPTIONS: {'options': '-c search_path=app'}`)

---

## [v1.0.0] - Versión Inicial
- Setup inicial del proyecto Django
- Modelos base: Users, Roles, Routes, Permissions
- WebViews para Panel, Login, Register
- Controllers y Services para gestión de permisos
- Integración Google OAuth
