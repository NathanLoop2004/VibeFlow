"""
authController.py - Controlador para autenticación (login).
Estructura de clase con métodos estáticos (estilo Express.js).
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from VibeFlow.Public.Services import usersService, rolesService, userRolesService


class AuthController:

    @staticmethod
    @csrf_exempt
    def login(request):
        """POST: Autentica un usuario con username y password."""
        try:
            body = json.loads(request.body)

            username = body.get("username")
            password = body.get("password")

            if not username or not password:
                return JsonResponse({
                    "status": False,
                    "message": "Username y password son requeridos"
                }, status=400)

            usuario = usersService.authenticate_user(username, password)

            if not usuario:
                return JsonResponse({
                    "status": False,
                    "message": "Credenciales inválidas o usuario inactivo"
                }, status=401)

            # Guardar sesión (como Express req.session.user)
            request.session['user'] = usuario
            request.session['is_authenticated'] = True

            return JsonResponse({
                "status": True,
                "data": usuario,
                "message": "Login exitoso"
            })
        except Exception as e:
            print(f"Error en login: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def logout(request):
        """POST: Cierra la sesión del usuario."""
        request.session.flush()
        return JsonResponse({
            "status": True,
            "message": "Sesión cerrada correctamente"
        })

    @staticmethod
    @csrf_exempt
    def register(request):
        """POST: Registra un nuevo usuario y le asigna el rol usuario_normal."""
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

            # Verificar si el username ya existe
            existing = usersService.get_user_by_username(username)
            if existing:
                return JsonResponse({
                    "status": False,
                    "message": "El nombre de usuario ya está en uso"
                }, status=409)

            # Verificar si el email ya existe
            existing_email = usersService.get_user_by_email(email)
            if existing_email:
                return JsonResponse({
                    "status": False,
                    "message": "El email ya está registrado"
                }, status=409)

            # Crear el usuario
            result = usersService.create_user({
                "username": username,
                "email": email,
                "password": password,
            })

            # Buscar el rol usuario_normal y asignarlo
            rol = rolesService.get_role_by_name("usuario_normal")
            if rol:
                userRolesService.assign_role({
                    "user_id": result["id"],
                    "role_id": rol["id"],
                })

            return JsonResponse({
                "status": True,
                "data": result,
                "message": "Usuario registrado exitosamente"
            }, status=201)
        except Exception as e:
            print(f"Error en register: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)
