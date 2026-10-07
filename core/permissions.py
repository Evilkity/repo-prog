from rest_framework import permissions
from .services import MembershipService


class IsProjectAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado:
    - Métodos seguros (GET, HEAD, OPTIONS): solo miembros del proyecto.
    - Métodos de escritura (POST, PUT, PATCH, DELETE): solo administradores del proyecto.
    """

    def has_object_permission(self, request, view, obj):
        project = obj if hasattr(obj, "memberships") else obj.project

        # Métodos de solo lectura: cualquier miembro
        if request.method in permissions.SAFE_METHODS:
            return MembershipService.is_member(request.user, project)

        # Métodos de escritura: solo administradores
        return MembershipService.is_admin(request.user, project)
