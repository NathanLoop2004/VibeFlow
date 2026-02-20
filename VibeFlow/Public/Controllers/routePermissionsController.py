"""
routePermissionsController.py - Controlador para gestionar permisos de rutas.
Los permisos se asignan por ROL (no por usuario).
Estructura de clase con métodos estáticos (estilo Express.js).
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from VibeFlow.Public.Services import routePermissionsService


class RoutePermissionsController:

    @staticmethod
    @csrf_exempt
    def obtener_permisos(request):
        """GET: Obtiene todos los permisos."""
        try:
            permisos = routePermissionsService.get_all_permissions()

            print("=== JSON route-permissions ===")
            print(json.dumps(permisos, indent=2, default=str))
            print("==============================")

            return JsonResponse({
                "status": True,
                "data": permisos,
                "message": "Permisos obtenidos correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_permisos: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def obtener_permisos_por_ruta(request, route_id):
        """GET: Obtiene los permisos de una ruta específica."""
        try:
            permisos = routePermissionsService.get_permissions_by_route(route_id)

            return JsonResponse({
                "status": True,
                "data": permisos,
                "message": "Permisos de la ruta obtenidos correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_permisos_por_ruta: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def obtener_permisos_por_rol(request, role_id):
        """GET: Obtiene los permisos de un rol."""
        try:
            permisos = routePermissionsService.get_permissions_by_role(role_id)

            return JsonResponse({
                "status": True,
                "data": permisos,
                "message": "Permisos del rol obtenidos correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_permisos_por_rol: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def crear_permiso(request):
        """POST: Crea un nuevo permiso."""
        try:
            body = json.loads(request.body)

            role_id = body.get("role_id")
            route_id = body.get("route_id")

            if not role_id or not route_id:
                return JsonResponse({
                    "status": False,
                    "message": "role_id y route_id son requeridos"
                }, status=400)

            resultado = routePermissionsService.create_permission(body)

            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Permiso creado correctamente"
            }, status=201)
        except ValueError as e:
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=400)
        except Exception as e:
            print(f"Error en crear_permiso: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def actualizar_permiso(request, perm_id):
        """PUT: Actualiza un permiso existente."""
        try:
            body = json.loads(request.body)

            resultado = routePermissionsService.update_permission(perm_id, body)

            if not resultado:
                return JsonResponse({
                    "status": False,
                    "message": "Permiso no encontrado o sin cambios"
                }, status=404)

            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Permiso actualizado correctamente"
            })
        except Exception as e:
            print(f"Error en actualizar_permiso: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def eliminar_permiso(request, perm_id):
        """DELETE: Elimina un permiso."""
        try:
            eliminado = routePermissionsService.delete_permission(perm_id)

            if not eliminado:
                return JsonResponse({
                    "status": False,
                    "message": "Permiso no encontrado"
                }, status=404)

            return JsonResponse({
                "status": True,
                "data": {"id": perm_id},
                "message": "Permiso eliminado correctamente"
            })
        except Exception as e:
            print(f"Error en eliminar_permiso: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)
