from datetime import date, timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Project, ProjectMembership, Task
from .services import TaskService, ProjectService, MembershipService


class TaskFlowAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Usuarios de prueba
        self.admin_user = User.objects.create_user(username="admin_user", password="password123")
        self.member_user = User.objects.create_user(username="member_user", password="password123")
        self.other_user = User.objects.create_user(username="other_user", password="password123")

        # Proyecto de prueba
        self.project = Project.objects.create(name="Proyecto Alpha", description="Descripción de prueba")

        # Membresías
        ProjectMembership.objects.create(project=self.project, user=self.admin_user, role="admin")
        ProjectMembership.objects.create(project=self.project, user=self.member_user, role="miembro")

    def test_health_check_endpoints(self):
        """Verifica que los endpoints públicos de salud respondan correctamente."""
        res1 = self.client.get("/api/health/")
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.json()["status"], "ok")

        res2 = self.client.get("/api/health/version/")
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.json()["version"], "0.1.0")

    def test_user_registration(self):
        """Verifica el registro de usuarios vía API."""
        res = self.client.post("/api/register/", {
            "username": "nuevo_usuario",
            "password": "segurapassword123",
            "email": "nuevo@test.com"
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="nuevo_usuario").exists())

    def test_jwt_authentication_required(self):
        """Verifica que peticiones no autenticadas sean rechazadas con 401."""
        res = self.client.get("/api/projects/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_membership_and_permissions(self):
        """Verifica visibilidad de proyectos y permisos por rol."""
        # Miembro puede ver el proyecto
        self.client.force_authenticate(user=self.member_user)
        res = self.client.get(f"/api/projects/{self.project.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Miembro NO puede crear tareas (solo admin)
        res_post = self.client.post("/api/tasks/", {
            "project": self.project.id,
            "title": "Tarea intento por miembro",
            "due_date": str(date.today() + timedelta(days=5))
        })
        self.assertEqual(res_post.status_code, status.HTTP_403_FORBIDDEN)

        # Admin sí puede crear tareas
        self.client.force_authenticate(user=self.admin_user)
        res_admin = self.client.post("/api/tasks/", {
            "project": self.project.id,
            "title": "Tarea creada por admin",
            "due_date": str(date.today() + timedelta(days=5))
        })
        self.assertEqual(res_admin.status_code, status.HTTP_201_CREATED)

    def test_business_validation_cannot_complete_without_due_date(self):
        """Regla: no se puede marcar tarea como completada sin due_date."""
        self.client.force_authenticate(user=self.admin_user)
        task = Task.objects.create(
            project=self.project,
            title="Tarea sin fecha",
            status="pendiente",
            due_date=None,
            owner=self.admin_user
        )
        res = self.client.patch(f"/api/tasks/{task.id}/", {"status": "completada"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.json())

    def test_business_validation_en_progreso_requires_completed_task(self):
        """Regla Clase 4b: en_progreso requiere al menos una tarea previa completada en el proyecto."""
        self.client.force_authenticate(user=self.admin_user)
        # Intento de crear en_progreso directamente
        res = self.client.post("/api/tasks/", {
            "project": self.project.id,
            "title": "Tarea que quiere arrancar en progreso",
            "status": "en_progreso",
            "due_date": str(date.today() + timedelta(days=3))
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Ahora creamos y completamos una tarea válida
        t1 = Task.objects.create(
            project=self.project,
            title="Tarea previa completada",
            status="pendiente",
            due_date=date.today() + timedelta(days=2),
            owner=self.admin_user
        )
        TaskService.mark_completed(t1)

        # Ahora sí debe permitir crear otra tarea en_progreso
        res2 = self.client.post("/api/tasks/", {
            "project": self.project.id,
            "title": "Segunda tarea ahora sí en progreso",
            "status": "en_progreso",
            "due_date": str(date.today() + timedelta(days=4))
        })
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)

    def test_project_summary_action(self):
        """Verifica la acción custom de resumen del proyecto (Tarea Clase 5)."""
        self.client.force_authenticate(user=self.admin_user)
        Task.objects.create(project=self.project, title="T1", status="pendiente", owner=self.admin_user)
        Task.objects.create(project=self.project, title="T2", status="completada", due_date=date.today(), owner=self.admin_user)

        res = self.client.get(f"/api/projects/{self.project.id}/summary/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["pendiente"], 1)
        self.assertEqual(data["completada"], 1)
        self.assertEqual(data["total"], 2)

    def test_add_member_action(self):
        """Verifica la acción custom de agregar miembros (Tarea Clase 7)."""
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.post(f"/api/projects/{self.project.id}/add_member/", {
            "username": self.other_user.username,
            "role": "miembro"
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(MembershipService.is_member(self.other_user, self.project))
