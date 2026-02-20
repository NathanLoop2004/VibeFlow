"""
authController.py - Controlador para autenticación (login).
Estructura de clase con métodos estáticos (estilo Express.js).
"""

import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from VibeFlow.Public.Services import usersService, rolesService, userRolesService, routePermissionsService
from VibeFlow.Public.Services import jwtService
from VibeFlow.Public.Services import googleAuthService


class AuthController:

    @staticmethod
    @csrf_exempt
    def login(request):
        """POST: Autentica un usuario con username y password."""
        try:
            body = json.loads(request.body)

            username = body.get("username", "").strip()
            password = body.get("password")

            # Si el usuario ingresó un email, normalizarlo a minúsculas
            if "@" in username:
                username = username.lower()

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

            # Obtener roles del usuario
            user_roles = userRolesService.get_roles_by_user(usuario['id'])

            # Generar token JWT con roles
            token = jwtService.generate_token(usuario, roles=user_roles)

            # Guardar sesión (compatibilidad con vistas server-side)
            request.session['user'] = usuario
            request.session['is_authenticated'] = True

            return JsonResponse({
                "status": True,
                "data": usuario,
                "token": token,
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

            username = body.get("username", "").strip()
            email = body.get("email", "").strip().lower()
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

    @staticmethod
    @csrf_exempt
    def my_routes(request):
        """GET: Devuelve las rutas que el usuario en sesión puede ver (can_get=true)."""
        try:
            # Intentar JWT primero, luego sesión
            user = None
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                payload = jwtService.verify_token(token)
                if payload:
                    user = {'id': payload['user_id'], 'username': payload['username']}

            if not user:
                user = request.session.get('user')

            if not user:
                return JsonResponse({
                    "status": False,
                    "message": "No autorizado"
                }, status=401)

            user_id = user.get('id')
            permisos = routePermissionsService.get_permissions_by_user(str(user_id))

            # Filtrar solo las rutas con can_get = True
            rutas = [
                {
                    "route_id": p['route_id'],
                    "url_path": p['url_path'],
                    "route_name": p['route_name'],
                    "can_get": p['can_get'],
                    "can_post": p['can_post'],
                    "can_put": p['can_put'],
                    "can_delete": p['can_delete'],
                    "module_id": p.get('module_id'),
                    "module_name": p.get('module_name'),
                    "module_icon": p.get('module_icon'),
                    "module_order": p.get('module_order'),
                    "family_id": p.get('family_id'),
                    "family_name": p.get('family_name'),
                    "family_icon": p.get('family_icon'),
                    "family_order": p.get('family_order'),
                    "subfamily_id": p.get('subfamily_id'),
                    "subfamily_name": p.get('subfamily_name'),
                    "subfamily_icon": p.get('subfamily_icon'),
                    "subfamily_order": p.get('subfamily_order'),
                }
                for p in permisos if p.get('can_get')
            ]

            return JsonResponse({
                "status": True,
                "data": rutas,
                "message": "Rutas del usuario obtenidas correctamente"
            })
        except Exception as e:
            print(f"Error en my_routes: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def google_login(request):
        """
        POST: Autentica o registra un usuario usando Google OAuth.
        Recibe { credential: "token_de_google" }
        - Si el email ya existe → login directo
        - Si no existe → crea usuario + asigna rol usuario_normal → login
        """
        try:
            body = json.loads(request.body)
            credential = body.get("credential", "")

            if not credential:
                return JsonResponse({
                    "status": False,
                    "message": "Token de Google requerido"
                }, status=400)

            # Verificar token con Google
            google_user = googleAuthService.verify_google_token(credential)
            if not google_user:
                return JsonResponse({
                    "status": False,
                    "message": "Token de Google inválido o expirado"
                }, status=401)

            email = google_user['email'].lower()
            name = google_user['name']

            if not email:
                return JsonResponse({
                    "status": False,
                    "message": "No se pudo obtener el email de Google"
                }, status=400)

            # Buscar si el usuario ya existe por email
            usuario = usersService.get_user_by_email(email)

            if usuario:
                # Usuario existe → login directo
                if not usuario.get('is_active', True):
                    return JsonResponse({
                        "status": False,
                        "message": "Tu cuenta está desactivada"
                    }, status=403)
            else:
                # Usuario nuevo → registrar
                base_username = name.replace(' ', '_').lower() if name else email.split('@')[0]
                username = base_username

                # Si el username ya existe, agregar un sufijo
                existing = usersService.get_user_by_username(username)
                if existing:
                    username = f"{base_username}_{str(uuid.uuid4())[:6]}"

                # Crear usuario con contraseña aleatoria (usa Google para auth)
                random_pass = str(uuid.uuid4())
                result = usersService.create_user({
                    "username": username,
                    "email": email,
                    "password": random_pass,
                    "is_verified": True,
                })

                # Asignar rol usuario_normal
                rol = rolesService.get_role_by_name("usuario_normal")
                if rol:
                    userRolesService.assign_role({
                        "user_id": result["id"],
                        "role_id": rol["id"],
                    })

                # Obtener el usuario recién creado
                usuario = usersService.get_user_by_id(result["id"])

            # Obtener roles y generar JWT
            user_roles = userRolesService.get_roles_by_user(usuario['id'])
            token = jwtService.generate_token(usuario, roles=user_roles)

            # Guardar sesión
            request.session['user'] = usuario
            request.session['is_authenticated'] = True

            return JsonResponse({
                "status": True,
                "data": usuario,
                "token": token,
                "message": "Login con Google exitoso"
            })
        except Exception as e:
            print(f"Error en google_login: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)
