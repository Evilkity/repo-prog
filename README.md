# TaskFlow API

API REST desarrollada con **Python**, **Django** y **Django REST Framework (DRF)** para la gestión colaborativa de proyectos y tareas, construida de forma incremental a lo largo de las clases de la materia **Programación IV** (Tecnicatura Universitaria en Programación).

---

## 📋 Mapeo y Guía de Clases para el Docente

Este repositorio está estructurado para que el docente pueda verificar tanto el **código final integrado** como la **evolución clase por clase** de la materia.

El avance se puede auditar de dos maneras:
1. **En la rama `main`:** Contiene el proyecto completo, funcional y con todas las consignas y tareas domiciliarias resueltas e integradas.
2. **Mediante los Git Tags o el historial de Git (`git log`):** Cada clase y tarea cuenta con su propio commit y etiqueta (tag) en el repositorio para revisar el estado exacto del código en cada fecha.

### Tabla de Contenidos Desarrollados por Clase

| Clase / Módulo | Tema Principal | Archivos y Componentes Clave | Tarea para la Casa Desarrollada | Tag de Git |
| :--- | :--- | :--- | :--- | :---: |
| **Práctica Inicial** (PDFs Clase 1) | Repaso de Python, estructuras de datos, lectura de archivos CSV/JSON y validación de tipos | `practica_inicial/app.py`<br>`practica_inicial/validar_productos.py`<br>`practica_inicial/datos.csv` | Modularización del validador de datos con manejo de excepciones controladas | [`clase-01`](https://github.com/Evilkity/repo-prog/releases/tag/clase-01) |
| **Clase 1** (Unidad 1) | Entorno virtual (`venv`), arquitectura cliente-servidor, settings con `.env` y primer endpoint | `config/settings.py`<br>`core/views.py`<br>`core/urls.py`<br>`.env.example` | Endpoint `GET /api/health/version/` que retorna `{"version": "0.1.0"}` | [`clase-01`](https://github.com/Evilkity/repo-prog/releases/tag/clase-01) |
| **Clase 2** (Unidad 1) | E/S de datos en JSON, CSV y XML. Primer modelo `Task` y comando de importación | `core/models.py`<br>`core/management/commands/import_tasks.py`<br>`data/tasks_provider_a.json`<br>`data/tasks_provider_b.csv`<br>`data/tasks_provider_c.xml` | Soporte para proveedor D (`data/tasks_provider_d.json`) con registro inválido sin título y logging en `import.log` | [`clase-02`](https://github.com/Evilkity/repo-prog/releases/tag/clase-02) |
| **Clase 3** (Unidad 2) | Principios REST, modelado relacional (`Project`, `Task`, `Tag`), serializers anidados y optimización N+1 | `core/models.py`<br>`core/serializers.py`<br>`core/views.py`<br>`core/urls.py` | Vista de detalle de un proyecto puntual `GET /api/projects/<int:project_id>/` usando `get_object_or_404` | [`clase-03`](https://github.com/Evilkity/repo-prog/releases/tag/clase-03) |
| **Clase 4** (Unidad 2) | CRUD completo con `ModelViewSet`, `DefaultRouter`, códigos de estado HTTP y manejo de errores centralizado | `core/views.py`<br>`core/exceptions.py`<br>`core/serializers.py` | Regla en `TaskSerializer`: no completar sin fecha límite (`validate_due_date` y `validate`) | [`clase-04`](https://github.com/Evilkity/repo-prog/releases/tag/clase-04) |
| **Clase 4b** (Resolución Tarea) | Reglas de negocio avanzadas, soporte en `PATCH` (`self.instance`) y registro de respuestas con `curl` | `core/serializers.py`<br>`respuestas_http.txt` | Validación: `en_progreso` exige que el proyecto tenga al menos una tarea completada. Archivo `respuestas_http.txt` con códigos 200, 201, 204, 400, 404 y 500 | [`clase-04b`](https://github.com/Evilkity/repo-prog/releases/tag/clase-04b) |
| **Clase 5** (Unidad 2) | Capa de servicios y repositorios, paginación, filtros (`django-filter`) e integración externa de feriados | `core/repositories.py`<br>`core/services.py`<br>`core/views.py`<br>`config/settings.py` | Servicio `ProjectService.project_summary` y acción `@action` en `GET /api/projects/<id>/summary/` con conteo de tareas | [`clase-05`](https://github.com/Evilkity/repo-prog/releases/tag/clase-05) |
| **Clase 6** (Unidad 3) | Autenticación con JWT (`simplejwt`), registro de usuarios y propiedad de recursos (`owner`) | `config/settings.py`<br>`config/urls.py`<br>`core/models.py`<br>`core/serializers.py`<br>`core/views.py` | Pruebas de ciclo de vida del JWT, refresh token y aislamiento de datos por usuario (`get_queryset` y `perform_create`) | [`clase-06`](https://github.com/Evilkity/repo-prog/releases/tag/clase-06) |
| **Clase 7** (Unidad 3) | Roles y colaboración (`ProjectMembership`), permisos personalizados (`IsProjectAdminOrReadOnly`) y OAuth 2.0 social | `core/models.py`<br>`core/permissions.py`<br>`core/services.py`<br>`docs/flujo_oauth.md`<br>`config/settings.py` | Acción `POST /api/projects/<id>/add_member/` para agregar colaboradores por rol y documento explicativo del flujo OAuth 2.0 | [`clase-07`](https://github.com/Evilkity/repo-prog/releases/tag/clase-07) |

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
repo-prog/
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
│   └── flujo_oauth.md
├── practica_inicial/        # Ejercicios iniciales de repaso de Python (Clase 1)
│   ├── app.py
│   ├── validar_productos.py
│   ├── datos.csv
│   └── salida.json
├── respuestas_http.txt      # Respuestas de códigos de estado probadas con curl (Clase 4b)
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
.\\venv\\Scripts\\Activate.ps1
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
| `GET` | `/api/health/version/` | Versión actual de la API (Tarea Clase 1) | Público |
| `POST` | `/api/register/` | Registro de nuevo usuario (Clase 6) | Público |
| `POST` | `/api/token/` | Login: obtiene par JWT (`access` y `refresh`) (Clase 6) | Público |
| `POST` | `/api/token/refresh/`| Obtiene nuevo `access` token usando `refresh` (Clase 6) | Público |
| `GET` / `POST` | `/api/projects/` | Listar y crear proyectos (Clase 4 y 7) | Autenticado |
| `GET` / `PUT` / `DELETE` | `/api/projects/<id>/` | Detalle, edición y borrado de proyecto (Clase 4 y 7) | Admin / Miembro |
| `GET` | `/api/projects/<id>/summary/` | Resumen de tareas por estado (Tarea Clase 5) | Miembros |
| `POST` | `/api/projects/<id>/add_member/` | Agregar colaborador al proyecto (Tarea Clase 7) | Admin |
| `GET` / `POST` | `/api/tasks/` | Listar y crear tareas (Clase 4, 6 y 7) | Admin / Miembro |
| `GET` / `PUT` / `DELETE` | `/api/tasks/<id>/` | Detalle, edición y borrado de tarea (Clase 4 y 7) | Admin / Miembro |
| `POST` | `/api/tasks/<id>/complete/` | Marcar tarea como completada (Clase 5) | Admin |
| `GET` | `/api/tasks/overdue/` | Tareas vencidas paginadas (Clase 5) | Miembros |
| `GET` | `/api/auth/social/jwt/` | Entrega par JWT tras login OAuth con Google (Clase 7) | Autenticado |

---

## Ejecutar Pruebas Automatizadas

Para correr la suite completa de pruebas:
```bash
python manage.py test core
```
