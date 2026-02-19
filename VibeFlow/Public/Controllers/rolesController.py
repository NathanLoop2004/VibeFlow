"""
rolesController.py - Controlador para gestionar roles.
Estructura de clase con métodos estáticos (estilo Express.js).
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from VibeFlow.Public.Services import rolesService


class RolesController:

    @staticmethod
    @csrf_exempt
    def obtener_roles(request):
        """GET: Obtiene todos los roles."""
        try:
            roles = rolesService.get_all_roles()

            return JsonResponse({
                "status": True,
                "data": roles,
                "message": "Roles obtenidos correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_roles: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def obtener_rol_por_id(request, role_id):
        """GET: Obtiene un rol por su ID."""
        try:
            rol = rolesService.get_role_by_id(role_id)

            if not rol:
                return JsonResponse({
                    "status": False,
                    "message": "Rol no encontrado"
                }, status=404)

            return JsonResponse({
                "status": True,
                "data": rol
            })
        except Exception as e:
            print(f"Error en obtener_rol_por_id: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def crear_rol(request):
        """POST: Crea un nuevo rol."""
        try:
            body = json.loads(request.body)

            name = body.get("name")
            if not name:
                return JsonResponse({
                    "status": False,
                    "message": "Nombre es requerido"
                }, status=400)

            resultado = rolesService.create_role(body)

            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Rol creado correctamente"
            }, status=201)
        except Exception as e:
            print(f"Error en crear_rol: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def actualizar_rol(request, role_id):
        """PUT: Actualiza un rol por su ID."""
        try:
            body = json.loads(request.body)

            resultado = rolesService.update_role(role_id, body)

            if not resultado:
                return JsonResponse({
                    "status": False,
                    "message": "Rol no encontrado o sin cambios"
                }, status=404)

            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Rol actualizado correctamente"
            })
        except Exception as e:
            print(f"Error en actualizar_rol: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def eliminar_rol(request, role_id):
        """DELETE: Elimina un rol por su ID."""
        try:
            eliminado = rolesService.delete_role(role_id)

            if not eliminado:
                return JsonResponse({
                    "status": False,
                    "message": "Rol no encontrado"
                }, status=404)

            return JsonResponse({
                "status": True,
                "data": {"id": role_id},
                "message": "Rol eliminado correctamente"
            })
        except Exception as e:
            print(f"Error en eliminar_rol: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)
