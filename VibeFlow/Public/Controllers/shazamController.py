"""
shazamController.py - Controlador para el Shazam MVP.
Endpoints: listar canciones, subir canción, generar fingerprints, buscar.
"""

import json
import base64
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from VibeFlow.Public.Services import songsService
from VibeFlow.Public.Services import fingerprintService


class ShazamController:

    @staticmethod
    @csrf_exempt
    def obtener_canciones(request):
        """GET: Lista todas las canciones."""
        try:
            canciones = songsService.get_all_songs()
            return JsonResponse({
                "status": True,
                "data": canciones,
                "message": "Canciones obtenidas correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_canciones: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def obtener_cancion(request, song_id):
        """GET: Obtiene una canción por ID."""
        try:
            cancion = songsService.get_song_by_id(song_id)
            if not cancion:
                return JsonResponse({"status": False, "message": "Canción no encontrada"}, status=404)
            return JsonResponse({"status": True, "data": cancion})
        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def subir_cancion(request):
        """
        POST: Sube una canción y genera fingerprints automáticamente.
        Body JSON: { title, artist, audio_base64 (WAV), file_type, file_size, duration_seconds }
        El frontend convierte cualquier formato a WAV antes de enviar.
        """
        try:
            body = json.loads(request.body)

            title = body.get("title", "").strip()
            audio_b64 = body.get("audio_base64", "")

            if not title:
                return JsonResponse({"status": False, "message": "El título es requerido"}, status=400)
            if not audio_b64:
                return JsonResponse({"status": False, "message": "El audio es requerido"}, status=400)

            # 1. Crear la canción en BD
            result = songsService.create_song(body)
            song_id = result['id']

            # 2. Decodificar audio y generar fingerprints
            wav_bytes = base64.b64decode(audio_b64)
            fps = fingerprintService.generate_fingerprints(wav_bytes)

            # 3. Guardar fingerprints
            fp_count = fingerprintService.store_fingerprints(song_id, fps)

            return JsonResponse({
                "status": True,
                "data": {
                    "song_id": song_id,
                    "fingerprints_generated": fp_count
                },
                "message": f"Canción subida con {fp_count} fingerprints generados"
            }, status=201)

        except ValueError as e:
            return JsonResponse({"status": False, "message": str(e)}, status=400)
        except Exception as e:
            print(f"Error en subir_cancion: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def buscar_cancion(request):
        """
        POST: Busca una canción a partir de audio capturado.
        Body JSON: { audio_base64 (WAV de ~5 segundos) }
        """
        try:
            body = json.loads(request.body)
            audio_b64 = body.get("audio_base64", "")

            if not audio_b64:
                return JsonResponse({"status": False, "message": "El audio es requerido"}, status=400)

            # 1. Decodificar audio y generar fingerprints
            wav_bytes = base64.b64decode(audio_b64)
            fps = fingerprintService.generate_fingerprints(wav_bytes)

            if not fps:
                return JsonResponse({
                    "status": False,
                    "message": "No se pudieron generar fingerprints del audio. ¿El audio tiene sonido?"
                }, status=400)

            # 2. Buscar en BD
            result = fingerprintService.search_by_fingerprints(fps)

            if not result:
                return JsonResponse({
                    "status": True,
                    "data": None,
                    "message": "No se encontró ninguna coincidencia"
                })

            # Mensaje según nivel de confirmación
            if result['is_confirmed']:
                msg = (
                    f"¡Canción confirmada! \"{result['title']}\" de {result['artist']} "
                    f"({result['matched_hashes']}/{result['min_required']} matches, "
                    f"{result['confidence']}% confianza)"
                )
            else:
                msg = (
                    f"Posible coincidencia: \"{result['title']}\" de {result['artist']} "
                    f"({result['matched_hashes']}/{result['min_required']} matches necesarios, "
                    f"{result['confidence']}% confianza)"
                )

            return JsonResponse({
                "status": True,
                "data": result,
                "message": msg
            })

        except ValueError as e:
            return JsonResponse({"status": False, "message": str(e)}, status=400)
        except Exception as e:
            print(f"Error en buscar_cancion: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def eliminar_cancion(request, song_id):
        """DELETE: Elimina una canción y sus fingerprints."""
        try:
            songsService.delete_song(song_id)
            return JsonResponse({
                "status": True,
                "message": "Canción eliminada correctamente"
            })
        except ValueError as e:
            return JsonResponse({"status": False, "message": str(e)}, status=404)
        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def actualizar_cancion(request, song_id):
        """PUT: Actualiza título/artista de una canción."""
        try:
            body = json.loads(request.body)
            resultado = songsService.update_song(song_id, body)
            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Canción actualizada correctamente"
            })
        except ValueError as e:
            return JsonResponse({"status": False, "message": str(e)}, status=404)
        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def audio_cancion(request, song_id):
        """GET: Descarga/reproduce el audio de una canción."""
        try:
            result = songsService.get_song_audio(song_id)
            if not result or not result['audio_data']:
                return JsonResponse({"status": False, "message": "Audio no disponible"}, status=404)
            response = HttpResponse(result['audio_data'], content_type=result['file_type'])
            response['Content-Disposition'] = f'inline; filename="{result["title"]}.wav"'
            return response
        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def regenerar_cancion(request, song_id):
        """POST: Regenera fingerprints de una canción desde su audio guardado."""
        try:
            count = fingerprintService.regenerate_song(song_id)
            return JsonResponse({
                "status": True,
                "data": {"song_id": song_id, "fingerprints": count},
                "message": f"Fingerprints regenerados: {count}"
            })
        except ValueError as e:
            return JsonResponse({"status": False, "message": str(e)}, status=404)
        except Exception as e:
            import traceback; traceback.print_exc()
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def regenerar_todas(request):
        """POST: Regenera fingerprints de TODAS las canciones."""
        try:
            result = fingerprintService.regenerate_all()
            return JsonResponse({
                "status": True,
                "data": result,
                "message": f"Regeneración completa: {result['processed']} canciones procesadas"
            })
        except Exception as e:
            import traceback; traceback.print_exc()
            return JsonResponse({"status": False, "message": str(e)}, status=500)
