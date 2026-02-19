"""
userRolesController.py - Controlador para gestionar asignación de roles a usuarios.
Estructura de clase con métodos estáticos (estilo Express.js).
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from VibeFlow.Public.Services import userRolesService


class UserRolesController:

    @staticmethod
    @csrf_exempt
    def obtener_asignaciones(request):
        """GET: Obtiene todas las asignaciones usuario-rol."""
        try:
            asignaciones = userRolesService.get_all_user_roles()

            return JsonResponse({
                "status": True,
                "data": asignaciones,
                "message": "Asignaciones obtenidas correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_asignaciones: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def obtener_roles_por_usuario(request, user_id):
        """GET: Obtiene todos los roles de un usuario."""
        try:
            roles = userRolesService.get_roles_by_user(str(user_id))

            return JsonResponse({
                "status": True,
                "data": roles,
                "message": "Roles del usuario obtenidos correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_roles_por_usuario: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def obtener_usuarios_por_rol(request, role_id):
        """GET: Obtiene todos los usuarios que tienen un rol."""
        try:
            usuarios = userRolesService.get_users_by_role(role_id)

            return JsonResponse({
                "status": True,
                "data": usuarios,
                "message": "Usuarios con el rol obtenidos correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_usuarios_por_rol: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def asignar_rol(request):
        """POST: Asigna un rol a un usuario."""
        try:
            body = json.loads(request.body)

            user_id = body.get("user_id")
            role_id = body.get("role_id")

            if not user_id or not role_id:
                return JsonResponse({
                    "status": False,
                    "message": "user_id y role_id son requeridos"
                }, status=400)

            resultado = userRolesService.assign_role(body)

            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Rol asignado correctamente"
            }, status=201)
        except ValueError as e:
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=400)
        except Exception as e:
            print(f"Error en asignar_rol: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def eliminar_asignacion(request, user_id, role_id):
        """DELETE: Elimina la asignación de un rol a un usuario."""
        try:
            eliminado = userRolesService.remove_role(str(user_id), role_id)

            if not eliminado:
                return JsonResponse({
                    "status": False,
                    "message": "Asignación no encontrada"
                }, status=404)

            return JsonResponse({
                "status": True,
                "data": {"user_id": str(user_id), "role_id": role_id},
                "message": "Asignación eliminada correctamente"
            })
        except Exception as e:
            print(f"Error en eliminar_asignacion: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)
