"""
usersController.py - Controlador para gestionar usuarios.
Estructura de clase con métodos estáticos (estilo Express.js).
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from VibeFlow.Public.Services import usersService


class UsersController:

    @staticmethod
    @csrf_exempt
    def obtener_usuarios(request):
        """GET: Obtiene todos los usuarios."""
        try:
            usuarios = usersService.get_all_users()

            return JsonResponse({
                "status": True,
                "data": usuarios,
                "message": "Usuarios obtenidos correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_usuarios: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def obtener_usuario_por_id(request, user_id):
        """GET: Obtiene un usuario por su UUID."""
        try:
            usuario = usersService.get_user_by_id(str(user_id))

            if not usuario:
                return JsonResponse({
                    "status": False,
                    "message": "Usuario no encontrado"
                }, status=404)

            return JsonResponse({
                "status": True,
                "data": usuario
            })
        except Exception as e:
            print(f"Error en obtener_usuario_por_id: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def crear_usuario(request):
        """POST: Crea un nuevo usuario."""
        try:
            body = json.loads(request.body)

            username = body.get("username")
            email = body.get("email")
            password = body.get("password")

            if not username or not email or not password:
                return JsonResponse({
                    "status": False,
                    "message": "Username, email y password son requeridos"
                }, status=400)

            resultado = usersService.create_user(body)

            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Usuario creado correctamente"
            }, status=201)
        except Exception as e:
            print(f"Error en crear_usuario: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def actualizar_usuario(request, user_id):
        """PUT: Actualiza un usuario por su UUID."""
        try:
            body = json.loads(request.body)

            resultado = usersService.update_user(str(user_id), body)

            if not resultado:
                return JsonResponse({
                    "status": False,
                    "message": "Usuario no encontrado o sin cambios"
                }, status=404)

            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Usuario actualizado correctamente"
            })
        except Exception as e:
            print(f"Error en actualizar_usuario: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def eliminar_usuario(request, user_id):
        """DELETE: Elimina un usuario por su UUID."""
        try:
            eliminado = usersService.delete_user(str(user_id))

            if not eliminado:
                return JsonResponse({
                    "status": False,
                    "message": "Usuario no encontrado"
                }, status=404)

            return JsonResponse({
                "status": True,
                "data": {"id": str(user_id)},
                "message": "Usuario eliminado correctamente"
            })
        except Exception as e:
            print(f"Error en eliminar_usuario: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)
