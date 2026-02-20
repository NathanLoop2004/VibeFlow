"""
shazamConsumer.py - WebSocket consumer para streaming de audio en tiempo real.

Flujo:
1. El cliente abre ws://…/ws/shazam/  y envía chunks de audio PCM (binario).
2. Los chunks se acumulan en un buffer interno.
3. Cada ANALYSIS_INTERVAL segundos (o cuando el cliente envía {"action":"search"})
   el server genera fingerprints del audio acumulado, busca en la BD y envía
   el resultado al cliente.
4. Si se encuentra una coincidencia confirmada, se envía un mensaje final
   con is_confirmed=True y se cierra el WebSocket.

Mensajes JSON que envía el servidor al cliente:
  - {"type": "status",    "message": "..."}         → info / progreso
  - {"type": "partial",   "data": {...}}             → resultado parcial (no confirmado)
  - {"type": "confirmed", "data": {...}}             → canción confirmada (fin)
  - {"type": "no_match",  "message": "..."}          → búsqueda sin resultado
  - {"type": "error",     "message": "..."}          → error

Mensajes que acepta del cliente:
  - Binario (bytes)                    → chunk de audio WAV/PCM
  - {"action": "search"}               → forzar búsqueda con lo acumulado
  - {"action": "reset"}                → limpiar buffer
  - {"action": "stop"}                 → cerrar conexión
"""

import json
import traceback
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from VibeFlow.Public.Services import fingerprintService


# ── Cada cuántos bytes acumulados se lanza un análisis automático ──
# ~5 segundos de audio PCM 16-bit mono 11025 Hz ≈ 110 250 bytes
AUTO_ANALYSIS_BYTES = 110_250


class ShazamStreamConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer para identificación de audio en tiempo real."""

    async def connect(self):
        self.audio_buffer = bytearray()
        self.found = False
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'status',
            'message': 'Conexión WebSocket establecida. Envía audio para identificar.'
        }))

    async def disconnect(self, close_code):
        self.audio_buffer.clear()

    # ── Recepción de mensajes ──────────────────────────────────────────
    async def receive(self, text_data=None, bytes_data=None):
        # ── Mensaje binario: chunk de audio ──
        if bytes_data:
            if self.found:
                return  # Ya se encontró, ignorar más audio

            self.audio_buffer.extend(bytes_data)

            # Análisis automático cada AUTO_ANALYSIS_BYTES bytes
            if len(self.audio_buffer) >= AUTO_ANALYSIS_BYTES:
                await self._analyze()
            return

        # ── Mensaje de texto (JSON) ──
        if text_data:
            try:
                msg = json.loads(text_data)
            except json.JSONDecodeError:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'JSON inválido'
                }))
                return

            action = msg.get('action', '')

            if action == 'search':
                await self._analyze()

            elif action == 'reset':
                self.audio_buffer.clear()
                self.found = False
                await self.send(text_data=json.dumps({
                    'type': 'status',
                    'message': 'Buffer limpiado. Listo para nuevo audio.'
                }))

            elif action == 'stop':
                await self.close()

    # ── Análisis de audio ──────────────────────────────────────────────
    async def _analyze(self):
        if not self.audio_buffer:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'No hay audio en el buffer para analizar.'
            }))
            return

        await self.send(text_data=json.dumps({
            'type': 'status',
            'message': f'Analizando {len(self.audio_buffer)} bytes de audio...'
        }))

        try:
            wav_bytes = bytes(self.audio_buffer)
            result = await self._search_fingerprints(wav_bytes)

            if result is None:
                await self.send(text_data=json.dumps({
                    'type': 'no_match',
                    'message': 'Sin coincidencias por ahora. Sigue enviando audio...',
                    'buffer_size': len(self.audio_buffer),
                }))
                return

            if result['is_confirmed']:
                self.found = True
                await self.send(text_data=json.dumps({
                    'type': 'confirmed',
                    'data': result,
                    'message': (
                        f'¡Canción confirmada! "{result["title"]}" de {result["artist"]} '
                        f'({result["matched_hashes"]}/{result["min_required"]} matches, '
                        f'{result["confidence"]}% confianza)'
                    )
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'partial',
                    'data': result,
                    'message': (
                        f'Posible: "{result["title"]}" de {result["artist"]} '
                        f'({result["matched_hashes"]}/{result["min_required"]} matches, '
                        f'{result["confidence"]}% confianza). Sigue enviando audio...'
                    )
                }))

        except Exception as e:
            traceback.print_exc()
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error al analizar audio: {str(e)}'
            }))

    # ── Operación síncrona de BD ejecutada en thread pool ──────────────
    @database_sync_to_async
    def _search_fingerprints(self, wav_bytes):
        """Genera fingerprints y busca en BD (ejecutado en hilo separado)."""
        fps = fingerprintService.generate_fingerprints(wav_bytes)
        if not fps:
            return None
        return fingerprintService.search_by_fingerprints(fps)
