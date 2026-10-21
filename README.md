# TaskFlow API

API REST desarrollada con **Python**, **Django** y **Django REST Framework (DRF)** para la gestión colaborativa de proyectos y tareas, construida a lo largo de las clases de la materia **Programación IV** (Tecnicatura Universitaria en Programación).

---

## Características Principales

- **Arquitectura en Capas:**
  - **Presentación:** ViewSets (`ModelViewSet`), Serializers (`ModelSerializer`) y Routers (`DefaultRouter`).
  - **Lógica de Negocio:** Servicios dedicados (`TaskService`, `ProjectService`, `MembershipService`, `HolidayService`).
  - **Acceso a Datos:** Repositorios (`TaskRepository`) con optimización de consultas (`select_related`, `prefetch_related`).
- **Seguridad y Control de Acceso:**
  - Autenticación mediante **JWT** (`djangorestframework-simplejwt`) con tokens de acceso y refresco rotativo.
  - Soporte de autenticación federada (OAuth 2.0 con Google vía `django-allauth`).
  - Permisos granulares basados en roles (`admin` y `miembro`) mediante clase personalizada `IsProjectAdminOrReadOnly`.
- **Reglas de Negocio Validadas:**
  - Validación de fechas límite (no permite fechas en el pasado).
  - Integridad de flujo: una tarea no puede completarse sin fecha límite, ni pasar a `en_progreso` si su proyecto no tiene tareas previamente completadas.
  - Detección automática de feriados nacionales consumiendo API pública externa con caché en memoria.
- **Paginación, Filtros y Búsqueda:**
  - Paginación estándar de resultados (`PageNumberPagination`).
  - Filtrado por estado, prioridad y proyecto (`django-filter`).
  - Búsqueda textual sobre título y descripción (`SearchFilter`) y ordenamiento configurable (`OrderingFilter`).
- **Comandos Personalizados:**
  - Comando `python manage.py import_tasks` para importar datos desde múltiples formatos (JSON, CSV, XML) con manejo de errores y logging en archivo `import.log`.
- **Manejo Centralizado de Errores:**
  - Handler personalizado de excepciones (`core/exceptions.py`) que estandariza las respuestas de error en toda la API (`{"error": true, "detail": ...}`).

---

## Estructura del Proyecto

```text
taskflow/
├── config/                  # Configuración global del proyecto Django
│   ├── settings.py          # Configuración por entornos, DRF, JWT y Allauth
│   ├── urls.py              # Enrutador principal de endpoints
│   ├── wsgi.py
│   └── asgi.py
├── core/                    # Aplicación principal
│   ├── models.py            # Modelos Project, ProjectMembership, Tag, Task
│   ├── serializers.py       # Serializadores DRF con validaciones y campos calculados
│   ├── views.py             # ViewSets, vistas APIView y acciones personalizadas
│   ├── permissions.py       # Permisos personalizados (IsProjectAdminOrReadOnly)
│   ├── services.py          # Capa de negocio (Task, Project, Membership, Holiday)
│   ├── repositories.py      # Capa de acceso a datos y optimización de querysets
│   ├── exceptions.py        # Manejador centralizado de errores
│   ├── admin.py             # Registro de modelos en el panel de administración
│   ├── urls.py              # Rutas internas de la app core
│   ├── tests.py             # Suite completa de pruebas unitarias e integración
│   └── management/
│       └── commands/
│           └── import_tasks.py # Comando de importación multi-proveedor
├── data/                    # Archivos de datos de ejemplo (JSON, CSV, XML)
├── docs/                    # Documentación adicional (Diagrama de flujo OAuth 2.0)
├── practica_inicial/        # Ejercicios iniciales de repaso de Python (Clase 1)
├── manage.py
├── requirements.txt         # Dependencias congeladas
└── .env.example             # Plantilla de variables de entorno
```

---

## Requisitos Previos

- Python 3.10 o superior.
- Git.

---

## Instalación y Puesta en Marcha

### 1. Clonar el repositorio y entrar a la carpeta
```bash
git clone https://github.com/Evilkity/repo-prog.git
cd repo-prog
```

### 2. Crear y activar el entorno virtual
En Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```
En Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copiar el archivo `.env.example` a `.env`:
```bash
cp .env.example .env
```

### 5. Aplicar migraciones a la base de datos
```bash
python manage.py migrate
```

### 6. (Opcional) Importar datos de ejemplo
```bash
python manage.py import_tasks
```

### 7. Crear superusuario para el panel de administración
```bash
python manage.py createsuperuser
```

### 8. Ejecutar el servidor de desarrollo
```bash
python manage.py runserver
```

El servidor quedará disponible en `http://127.0.0.1:8000/`.

---

## Endpoints Principales de la API

| Método | Endpoint | Descripción | Acceso |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health/` | Health check del servicio | Público |
| `GET` | `/api/health/version/` | Versión actual de la API | Público |
| `POST` | `/api/register/` | Registro de nuevo usuario | Público |
| `POST` | `/api/token/` | Login: obtiene par JWT (`access` y `refresh`) | Público |
| `POST` | `/api/token/refresh/`| Obtiene nuevo `access` token usando `refresh` | Público |
| `GET` / `POST` | `/api/projects/` | Listar y crear proyectos | Autenticado |
| `GET` / `PUT` / `DELETE` | `/api/projects/<id>/` | Detalle, edición y borrado de proyecto | Admin / Miembro |
| `GET` | `/api/projects/<id>/summary/` | Resumen de tareas por estado | Miembros |
| `POST` | `/api/projects/<id>/add_member/` | Agregar colaborador al proyecto | Admin |
| `GET` / `POST` | `/api/tasks/` | Listar y crear tareas | Admin / Miembro |
| `GET` / `PUT` / `DELETE` | `/api/tasks/<id>/` | Detalle, edición y borrado de tarea | Admin / Miembro |
| `POST` | `/api/tasks/<id>/complete/` | Marcar tarea como completada | Admin |
| `GET` | `/api/tasks/overdue/` | Tareas vencidas paginadas | Miembros |
| `GET` | `/api/auth/social/jwt/` | Entrega par JWT tras login OAuth con Google | Autenticado |

---

## Ejecutar Pruebas Automatizadas

Para correr la suite completa de pruebas:
```bash
python manage.py test core
```
