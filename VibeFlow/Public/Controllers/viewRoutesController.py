"""
viewRoutesController.py - Controlador para gestionar rutas de vistas.
Estructura de clase con métodos estáticos (estilo Express.js).
Incluye el renderizado dinámico de templates desde la BD.
"""

import json
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from VibeFlow.Public.Services import viewRoutesService
from VibeFlow.Public.Services import routePermissionsService


class ViewRoutesController:

    # Rutas públicas que no requieren autenticación
    PUBLIC_ROUTES = ('', 'register')

    @staticmethod
    def dynamic_view(request, url_path):
        """
        Vista dinámica: busca el url_path en la BD y renderiza el template.
        - Rutas públicas (login, register): acceso libre.
        - Resto de rutas: requiere estar logueado (sesión activa).
        - route_permissions solo controla qué aparece en el navbar del panel.
        """
        try:
            # Normalizar: quitar trailing slash
            url_path = url_path.strip('/')

            route = viewRoutesService.get_route_by_path(url_path)

            if not route:
                raise Http404(f"Ruta '{url_path}' no encontrada o desactivada")

            # Rutas públicas: acceso sin autenticación
            if url_path not in ViewRoutesController.PUBLIC_ROUTES:
                # Para el resto, solo verificar que esté logueado
                user = request.session.get('user')
                if not user:
                    return JsonResponse({
                        "status": False,
                        "message": "Debes iniciar sesión para acceder"
                    }, status=401)

            return render(request, route['template_name'])
        except Http404:
            raise
        except Exception as e:
            print(f"Error en dynamic_view: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def obtener_rutas(request):
        """GET: Obtiene todas las rutas."""
        try:
            rutas = viewRoutesService.get_all_routes()

            return JsonResponse({
                "status": True,
                "data": rutas,
                "message": "Rutas obtenidas correctamente"
            })
        except Exception as e:
            print(f"Error en obtener_rutas: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def obtener_ruta_por_id(request, route_id):
        """GET: Obtiene una ruta por su ID."""
        try:
            # Usamos get_all y filtramos, o podríamos agregar un método al service
            rutas = viewRoutesService.get_all_routes()
            ruta = next((r for r in rutas if r['id'] == route_id), None)

            if not ruta:
                return JsonResponse({
                    "status": False,
                    "message": "Ruta no encontrada"
                }, status=404)

            return JsonResponse({
                "status": True,
                "data": ruta
            })
        except Exception as e:
            print(f"Error en obtener_ruta_por_id: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def crear_ruta(request):
        """POST: Crea una nueva ruta."""
        try:
            body = json.loads(request.body)

            url_path = body.get("url_path")
            template_name = body.get("template_name")
            name = body.get("name")

            if not url_path or not template_name or not name:
                return JsonResponse({
                    "status": False,
                    "message": "url_path, template_name y name son requeridos"
                }, status=400)

            resultado = viewRoutesService.create_route(body)

            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Ruta creada correctamente"
            }, status=201)
        except Exception as e:
            print(f"Error en crear_ruta: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def actualizar_ruta(request, route_id):
        """PUT: Actualiza una ruta por su ID."""
        try:
            body = json.loads(request.body)

            resultado = viewRoutesService.update_route(route_id, body)

            if not resultado:
                return JsonResponse({
                    "status": False,
                    "message": "Ruta no encontrada o sin cambios"
                }, status=404)

            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Ruta actualizada correctamente"
            })
        except Exception as e:
            print(f"Error en actualizar_ruta: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def eliminar_ruta(request, route_id):
        """DELETE: Elimina una ruta por su ID."""
        try:
            eliminado = viewRoutesService.delete_route(route_id)

            if not eliminado:
                return JsonResponse({
                    "status": False,
                    "message": "Ruta no encontrada"
                }, status=404)

            return JsonResponse({
                "status": True,
                "data": {"id": route_id},
                "message": "Ruta eliminada correctamente"
            })
        except Exception as e:
            print(f"Error en eliminar_ruta: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)

    @staticmethod
    @csrf_exempt
    def toggle_ruta(request, route_id):
        """PATCH: Activa/desactiva una ruta."""
        try:
            resultado = viewRoutesService.toggle_route(route_id)

            if not resultado:
                return JsonResponse({
                    "status": False,
                    "message": "Ruta no encontrada"
                }, status=404)

            return JsonResponse({
                "status": True,
                "data": resultado,
                "message": "Estado de ruta actualizado correctamente"
            })
        except Exception as e:
            print(f"Error en toggle_ruta: {e}")
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)
