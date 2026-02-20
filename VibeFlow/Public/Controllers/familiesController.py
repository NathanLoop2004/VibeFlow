"""
familiesController.py - Controlador para gestionar familias.
Estructura de clase con métodos estáticos (estilo Express.js).
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from VibeFlow.Public.Services import familiesService


class FamiliesController:

    @staticmethod
    @csrf_exempt
    def obtener_familias(request):
        """GET: Obtiene todas las familias."""
        try:
            familias = familiesService.get_all_families()
            return JsonResponse({
                "status": True,
                "data": familias,
                "message": "Familias obtenidas correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_familias: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def obtener_por_modulo(request, module_id):
        """GET: Obtiene familias de un módulo."""
        try:
            familias = familiesService.get_families_by_module(module_id)
            return JsonResponse({
                "status": True,
                "data": familias,
                "message": "Familias del módulo obtenidas correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_por_modulo: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def crear_familia(request):
        """POST: Crea una nueva familia."""
        try:
            body = json.loads(request.body)
            if not body.get("module_id") or not body.get("name"):
                return JsonResponse({"status": False, "message": "module_id y name son requeridos"}, status=400)

            resultado = familiesService.create_family(body)
            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Familia creada correctamente"
            }, status=201)
        except Exception as e:
            print(f"Error en crear_familia: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def actualizar_familia(request, family_id):
        """PUT: Actualiza una familia."""
        try:
            body = json.loads(request.body)
            resultado = familiesService.update_family(family_id, body)
            if not resultado:
                return JsonResponse({"status": False, "message": "Familia no encontrada"}, status=404)
            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Familia actualizada correctamente"
            })
        except Exception as e:
            print(f"Error en actualizar_familia: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def eliminar_familia(request, family_id):
        """DELETE: Elimina una familia."""
        try:
            eliminado = familiesService.delete_family(family_id)
            if not eliminado:
                return JsonResponse({"status": False, "message": "Familia no encontrada"}, status=404)
            return JsonResponse({
                "status": True,
                "data": {"id": family_id},
                "message": "Familia eliminada correctamente"
            })
        except Exception as e:
            print(f"Error en eliminar_familia: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)
