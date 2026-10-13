from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Project, ProjectMembership, Task
from .permissions import IsProjectAdminOrReadOnly
from .repositories import TaskRepository
from .serializers import ProjectSerializer, TaskSerializer, RegisterSerializer
from .services import TaskService, ProjectService, MembershipService


def health_check(request):
    return JsonResponse({"status": "ok", "service": "TaskFlow API"})


def health_version(request):
    return JsonResponse({"version": "0.1.0"})


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"mensaje": "Usuario registrado exitosamente."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SocialLoginJWTView(APIView):
    """
    Después de autenticarse con Google por allauth, genera y devuelve
    el par de tokens JWT correspondientes al usuario logueado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        refresh = RefreshToken.for_user(request.user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectAdminOrReadOnly]

    def get_queryset(self):
        return MembershipService.projects_for(self.request.user)

    def perform_create(self, serializer):
        project = serializer.save()
        ProjectMembership.objects.create(
            project=project,
            user=self.request.user,
            role="admin",
        )

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        project = self.get_object()
        data = ProjectService.project_summary(project)
        return Response(data)

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        """
        Tarea Clase 7: Agregar un miembro al proyecto.
        Solo un administrador del proyecto puede invocar esta acción.
        """
        project = self.get_object()
        if not MembershipService.is_admin(request.user, project):
            raise PermissionDenied("Solo los administradores del proyecto pueden agregar miembros.")

        username = request.data.get("username")
        role = request.data.get("role", "miembro")

        if not username:
            raise ValidationError({"username": ["Este campo es obligatorio."]})
        if role not in ("admin", "miembro"):
            raise ValidationError({"role": ["Rol inválido. Debe ser 'admin' o 'miembro'."]})

        user_to_add = get_object_or_404(User, username=username)

        if ProjectMembership.objects.filter(project=project, user=user_to_add).exists():
            return Response(
                {"error": True, "detail": "El usuario ya es miembro de este proyecto."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership = ProjectMembership.objects.create(
            project=project,
            user=user_to_add,
            role=role,
        )
        return Response(
            {
                "mensaje": f"Usuario {user_to_add.username} agregado al proyecto con rol {role}.",
                "membership_id": membership.id,
            },
            status=status.HTTP_201_CREATED,
        )


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filterset_fields = ["status", "priority", "project"]
    ordering_fields = ["due_date", "created_at", "priority"]
    search_fields = ["title", "description"]
    permission_classes = [IsAuthenticated, IsProjectAdminOrReadOnly]

    def get_queryset(self):
        return (
            TaskRepository.get_queryset()
            .filter(project__memberships__user=self.request.user)
            .distinct()
        )

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        if not MembershipService.is_admin(self.request.user, project):
            raise PermissionDenied(
                "Solo los administradores del proyecto pueden crear tareas."
            )
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        TaskService.mark_completed(task)
        return Response(self.get_serializer(task).data)

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        tasks = TaskService.tasks_overdue(self.get_queryset())
        page = self.paginate_queryset(tasks)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(tasks, many=True).data)
