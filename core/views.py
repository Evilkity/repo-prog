from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok", "service": "TaskFlow API"})

def health_version(request):
    """Tarea Clase 1: endpoint que devuelve la versión de la API."""
    return JsonResponse({"version": "0.1.0"})
