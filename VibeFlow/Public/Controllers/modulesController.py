"""
modulesController.py - Controlador para gestionar módulos.
Estructura de clase con métodos estáticos (estilo Express.js).
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from VibeFlow.Public.Services import modulesService


class ModulesController:

    @staticmethod
    @csrf_exempt
    def obtener_modulos(request):
        """GET: Obtiene todos los módulos."""
        try:
            modulos = modulesService.get_all_modules()
            return JsonResponse({
                "status": True,
                "data": modulos,
                "message": "Módulos obtenidos correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_modulos: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def crear_modulo(request):
        """POST: Crea un nuevo módulo."""
        try:
            body = json.loads(request.body)
            name = body.get("name")
            if not name:
                return JsonResponse({"status": False, "message": "name es requerido"}, status=400)

            resultado = modulesService.create_module(body)
            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Módulo creado correctamente"
            }, status=201)
        except Exception as e:
            print(f"Error en crear_modulo: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def actualizar_modulo(request, module_id):
        """PUT: Actualiza un módulo."""
        try:
            body = json.loads(request.body)
            resultado = modulesService.update_module(module_id, body)
            if not resultado:
                return JsonResponse({"status": False, "message": "Módulo no encontrado"}, status=404)
            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Módulo actualizado correctamente"
            })
        except Exception as e:
            print(f"Error en actualizar_modulo: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    @staticmethod
    @csrf_exempt
    def eliminar_modulo(request, module_id):
        """DELETE: Elimina un módulo."""
        try:
            eliminado = modulesService.delete_module(module_id)
            if not eliminado:
                return JsonResponse({"status": False, "message": "Módulo no encontrado"}, status=404)
            return JsonResponse({
                "status": True,
                "data": {"id": module_id},
                "message": "Módulo eliminado correctamente"
            })
        except Exception as e:
            print(f"Error en eliminar_modulo: {e}")
            return JsonResponse({"status": False, "message": str(e)}, status=500)
