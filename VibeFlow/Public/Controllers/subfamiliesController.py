"""
subfamiliesController.py - Controlador para gestionar subfamilias.
Estructura de clase con métodos estáticos (estilo Express.js).
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from VibeFlow.Public.Services import subfamiliesService


class SubfamiliesController:

    @staticmethod
    @csrf_exempt
    def obtener_subfamilias(request):
        """GET: Obtiene todas las subfamilias."""
        try:
            subfamilias = subfamiliesService.get_all_subfamilies()
            return JsonResponse({
                "status": True,
                "data": subfamilias,
                "message": "Subfamilias obtenidas correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_subfamilias: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def obtener_por_familia(request, family_id):
        """GET: Obtiene subfamilias de una familia."""
        try:
            subfamilias = subfamiliesService.get_subfamilies_by_family(family_id)
            return JsonResponse({
                "status": True,
                "data": subfamilias,
                "message": "Subfamilias de la familia obtenidas correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_por_familia: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def crear_subfamilia(request):
        """POST: Crea una nueva subfamilia."""
        try:
            body = json.loads(request.body)
            if not body.get("family_id") or not body.get("name"):
                return JsonResponse({"status": False, "message": "family_id y name son requeridos"}, status=400)

            resultado = subfamiliesService.create_subfamily(body)
            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Subfamilia creada correctamente"
            }, status=201)
        except Exception as e:
            print(f"Error en crear_subfamilia: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def actualizar_subfamilia(request, sf_id):
        """PUT: Actualiza una subfamilia."""
        try:
            body = json.loads(request.body)
            resultado = subfamiliesService.update_subfamily(sf_id, body)
            if not resultado:
                return JsonResponse({"status": False, "message": "Subfamilia no encontrada"}, status=404)
            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Subfamilia actualizada correctamente"
            })
        except Exception as e:
            print(f"Error en actualizar_subfamilia: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def eliminar_subfamilia(request, sf_id):
        """DELETE: Elimina una subfamilia."""
        try:
            eliminado = subfamiliesService.delete_subfamily(sf_id)
            if not eliminado:
                return JsonResponse({"status": False, "message": "Subfamilia no encontrada"}, status=404)
            return JsonResponse({
                "status": True,
                "data": {"id": sf_id},
                "message": "Subfamilia eliminada correctamente"
            })
        except Exception as e:
            print(f"Error en eliminar_subfamilia: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)
