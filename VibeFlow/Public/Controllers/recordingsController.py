"""
recordingsController.py - Controlador para gestionar grabaciones de audio.
Estructura de clase con métodos estáticos (estilo Express.js).
"""

import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from VibeFlow.Public.Services import recordingsService


class RecordingsController:

    @staticmethod
    @csrf_exempt
    def obtener_grabaciones(request):
        """GET: Obtiene todas las grabaciones (metadata sin audio)."""
        try:
            grabaciones = recordingsService.get_all_recordings()
            return JsonResponse({
                "status": True,
                "data": grabaciones,
                "message": "Grabaciones obtenidas correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_grabaciones: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def obtener_mis_grabaciones(request):
        """GET: Obtiene las grabaciones del usuario autenticado."""
        try:
            user = getattr(request, 'jwt_user', None)
            if not user:
                return JsonResponse({"status": False, "message": "No autorizado"}, status=401)

            grabaciones = recordingsService.get_recordings_by_user(user['user_id'])
            return JsonResponse({
                "status": True,
                "data": grabaciones,
                "message": "Grabaciones obtenidas correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_mis_grabaciones: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def obtener_grabacion_por_id(request, recording_id):
        """GET: Obtiene una grabación por su ID (metadata)."""
        try:
            grabacion = recordingsService.get_recording_by_id(recording_id)
            if not grabacion:
                return JsonResponse({"status": False, "message": "Grabación no encontrada"}, status=404)

            return JsonResponse({"status": True, "data": grabacion})
        except Exception as e:
            print(f"Error en obtener_grabacion_por_id: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def descargar_audio(request, recording_id):
        """GET: Descarga/reproduce el audio de una grabación."""
        try:
            result = recordingsService.get_recording_audio(recording_id)
            if not result or not result['audio_data']:
                return JsonResponse({"status": False, "message": "Audio no disponible"}, status=404)

            response = HttpResponse(result['audio_data'], content_type=result['file_type'])
            response['Content-Disposition'] = f'inline; filename="{result["name"]}"'
            return response
        except Exception as e:
            print(f"Error en descargar_audio: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def crear_grabacion(request):
        """POST: Crea una nueva grabación. Body JSON con audio_base64."""
        try:
            body = json.loads(request.body)

            name = body.get("name")
            audio_base64 = body.get("audio_base64")

            if not name:
                return JsonResponse({"status": False, "message": "El nombre es requerido"}, status=400)

            # Obtener user_id del JWT
            user = getattr(request, 'jwt_user', None)
            if not user:
                return JsonResponse({"status": False, "message": "No autorizado"}, status=401)

            body['user_id'] = user['user_id']

            resultado = recordingsService.create_recording(body)
            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Grabación guardada correctamente"
            }, status=201)
        except Exception as e:
            print(f"Error en crear_grabacion: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def actualizar_grabacion(request, recording_id):
        """PUT: Actualiza el nombre de una grabación."""
        try:
            body = json.loads(request.body)
            resultado = recordingsService.update_recording(recording_id, body)
            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Grabación actualizada correctamente"
            })
        except ValueError as e:
            return JsonResponse({"status": False, "message": str(e)}, status=404)
        except Exception as e:
            print(f"Error en actualizar_grabacion: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def eliminar_grabacion(request, recording_id):
        """DELETE: Elimina una grabación."""
        try:
            recordingsService.delete_recording(recording_id)
            return JsonResponse({
                "status": True,
                "message": "Grabación eliminada correctamente"
            })
        except ValueError as e:
            return JsonResponse({"status": False, "message": str(e)}, status=404)
        except Exception as e:
            print(f"Error en eliminar_grabacion: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)
