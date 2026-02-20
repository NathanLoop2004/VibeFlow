"""
teraboxService.py - Servicio de almacenamiento en TeraBox (1 TB gratis).

Guarda los archivos de audio en TeraBox en lugar de la BD para ahorrar
almacenamiento.  Solo los hashes (fingerprints) y metadatos se quedan en
Postgres.

Configuración requerida en .env:
    TERABOX_NDUS=<valor de la cookie ndus de tu sesión TeraBox>
    TERABOX_FOLDER=/VibeFlow/songs   (ruta remota donde se guardan los WAV)

Cómo obtener la cookie ndus:
    1. Abre https://www.terabox.com e inicia sesión.
    2. Abre DevTools → Application → Cookies → www.terabox.com
    3. Busca la cookie llamada "ndus" y copia su valor.
    4. Pégalo en tu .env como TERABOX_NDUS=...
"""

import os
import re
import json
import hashlib
import requests
from pathlib import PurePosixPath

# ── Configuración ──────────────────────────────────────────────────────
TERABOX_API    = 'https://www.terabox.com'
TERABOX_NDUS   = os.getenv('TERABOX_NDUS', '')
TERABOX_FOLDER = os.getenv('TERABOX_FOLDER', '/VibeFlow/songs')
APP_ID         = '250528'

_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/120.0.0.0 Safari/537.36'
)


class TeraBoxClient:
    """Cliente para la API de TeraBox."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': _USER_AGENT,
            'Accept': 'application/json',
        })
        self.session.cookies.set('ndus', TERABOX_NDUS, domain='.terabox.com')
        self._jstoken  = None
        self._bdstoken = None

    # ── Tokens internos ────────────────────────────────────────────────
    def _ensure_tokens(self):
        """Obtiene jsToken y bdstoken de la página principal de TeraBox."""
        if self._jstoken:
            return

        resp = self.session.get(f'{TERABOX_API}/main', timeout=15)
        resp.raise_for_status()

        m = re.search(r'"jsToken"\s*:\s*"([^"]+)"', resp.text)
        if m:
            self._jstoken = m.group(1)

        m = re.search(r'"bdstoken"\s*:\s*"([^"]+)"', resp.text)
        if m:
            self._bdstoken = m.group(1)

        if not self._jstoken:
            raise RuntimeError(
                'No se pudo obtener jsToken de TeraBox. '
                'Verifica que TERABOX_NDUS sea válido y no haya expirado.'
            )

    def _api_params(self, extra=None):
        params = {'app_id': APP_ID, 'jsToken': self._jstoken}
        if extra:
            params.update(extra)
        return params

    # ── Crear carpeta ──────────────────────────────────────────────────
    def _ensure_folder(self, folder_path):
        """Crea la carpeta remota si no existe."""
        self.session.post(
            f'{TERABOX_API}/api/create',
            params=self._api_params(),
            data={'path': folder_path, 'isdir': '1', 'size': '0',
                  'block_list': '[]'},
            timeout=15,
        )

    # ── Upload ─────────────────────────────────────────────────────────
    def upload(self, filename, data_bytes):
        """
        Sube un archivo a TeraBox.

        Args:
            filename:   nombre del archivo (ej: "42_cancion.wav")
            data_bytes: contenido binario del archivo

        Returns:
            str: ruta remota completa (ej: "/VibeFlow/songs/42_cancion.wav")
        """
        self._ensure_tokens()
        remote_path = f'{TERABOX_FOLDER}/{filename}'

        # Crear carpeta destino
        self._ensure_folder(TERABOX_FOLDER)

        # MD5 del archivo completo
        md5_full = hashlib.md5(data_bytes).hexdigest()

        # 1. Pre-create
        block_list = json.dumps([md5_full])
        resp = self.session.post(
            f'{TERABOX_API}/api/precreate',
            params=self._api_params(),
            data={
                'path': remote_path,
                'autoinit': '1',
                'target_path': TERABOX_FOLDER,
                'block_list': block_list,
                'local_mtime': '',
            },
            timeout=30,
        )
        resp.raise_for_status()
        pre = resp.json()

        if pre.get('errno', -1) != 0 and pre.get('return_type') != 2:
            raise RuntimeError(f'TeraBox precreate falló: {pre}')

        # Rapid upload (el archivo ya existe en la nube)
        if pre.get('return_type') == 2:
            print(f'[TeraBox] Rapid upload: {remote_path}')
            return remote_path

        uploadid = pre.get('uploadid', '')

        # 2. Subir chunk (archivo completo como un solo chunk)
        resp = self.session.post(
            f'{TERABOX_API}/rest/2.0/pcs/superfile2',
            params={
                'method': 'upload',
                'app_id': APP_ID,
                'jsToken': self._jstoken,
                'path': remote_path,
                'uploadid': uploadid,
                'partseq': '0',
            },
            files={'file': ('chunk', data_bytes)},
            timeout=120,
        )
        resp.raise_for_status()
        chunk_info = resp.json()
        chunk_md5 = chunk_info.get('md5', md5_full)

        # 3. Create (finalizar)
        resp = self.session.post(
            f'{TERABOX_API}/api/create',
            params=self._api_params(),
            data={
                'path': remote_path,
                'size': str(len(data_bytes)),
                'uploadid': uploadid,
                'target_path': TERABOX_FOLDER,
                'block_list': json.dumps([chunk_md5]),
                'local_mtime': '',
            },
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()

        if result.get('errno', -1) != 0:
            raise RuntimeError(f'TeraBox create falló: {result}')

        print(f'[TeraBox] Subido: {remote_path} ({len(data_bytes)} bytes)')
        return remote_path

    # ── Download ───────────────────────────────────────────────────────
    def get_download_url(self, remote_path):
        """Obtiene la URL de descarga directa (dlink) de un archivo."""
        self._ensure_tokens()
        resp = self.session.get(
            f'{TERABOX_API}/api/filemetas',
            params=self._api_params({
                'dlink': '1',
                'target': json.dumps([remote_path]),
            }),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get('list'):
            return data['list'][0].get('dlink', '')
        return ''

    def download(self, remote_path):
        """
        Descarga el contenido de un archivo desde TeraBox.

        Args:
            remote_path: ruta remota (ej: "/VibeFlow/songs/42_cancion.wav")

        Returns:
            bytes: contenido del archivo
        """
        dlink = self.get_download_url(remote_path)
        if not dlink:
            raise RuntimeError(f'No se obtuvo URL de descarga para: {remote_path}')

        resp = self.session.get(dlink, allow_redirects=True, timeout=120)
        resp.raise_for_status()
        return resp.content

    # ── Delete ─────────────────────────────────────────────────────────
    def delete(self, remote_path):
        """Elimina un archivo de TeraBox."""
        self._ensure_tokens()
        resp = self.session.post(
            f'{TERABOX_API}/api/filemanager',
            params=self._api_params({'opera': 'delete'}),
            data={'filelist': json.dumps([remote_path])},
            timeout=15,
        )
        resp.raise_for_status()
        result = resp.json()
        print(f'[TeraBox] Eliminado: {remote_path} → {result}')
        return result


# ── Singleton ──────────────────────────────────────────────────────────
_client = None


def get_client():
    """Retorna la instancia singleton del cliente TeraBox."""
    global _client
    if _client is None:
        if not TERABOX_NDUS:
            raise RuntimeError(
                'TERABOX_NDUS no configurado. '
                'Añade tu cookie ndus de TeraBox en el archivo .env'
            )
        _client = TeraBoxClient()
    return _client


def upload_song(song_id, title, wav_bytes):
    """
    Shortcut: sube un WAV a TeraBox con nombre normalizado.
    Retorna la ruta remota.
    """
    # Nombre seguro: id_titulo.wav
    safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')[:50]
    filename = f'{song_id}_{safe_title}.wav'
    return get_client().upload(filename, wav_bytes)


def download_song(remote_path):
    """Shortcut: descarga un WAV desde TeraBox."""
    return get_client().download(remote_path)


def delete_song(remote_path):
    """Shortcut: elimina un archivo de TeraBox."""
    return get_client().delete(remote_path)


def get_stream_url(remote_path):
    """Shortcut: obtiene URL directa de descarga/streaming."""
    return get_client().get_download_url(remote_path)
