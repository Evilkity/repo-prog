# Diagrama y Explicación del Flujo OAuth 2.0 (Authorization Code Flow)

Documento correspondiente a la **Tarea de la Clase 7** (Programación IV).

---

## 1. Diagrama de Secuencia

```
Usuario (Navegador)           Servidor Backend (TaskFlow)        Proveedor OAuth (Google)
       │                                   │                                 │
  (1)  │ ── Clic en "Login con Google" ──> │                                 │
       │                                   │                                 │
  (2)  │ <── Redirección (302) a Google ── │                                 │
       │     (client_id, scope, redirect_uri)                                │
       │                                                                     │
  (3)  │ ──────────────── Pantalla de consentimiento ──────────────────────> │
       │ <─────────────── El usuario autoriza acceso ─────────────────────── │
       │                                                                     │
  (4)  │ <── Redirección al callback con código temporal (?code=XYZ) ─────── │
       │                                                                     │
  (5)  │ ── Envía código a redirect_uri ─> │                                 │
       │                                   │                                 │
  (6)  │                                   │ ── Intercambia código por token ─> (Servidor a Servidor)
       │                                   │    (code + client_secret)       │
       │                                   │ <─ Devuelve Access Token OAuth ── │
       │                                   │                                 │
  (7)  │                                   │ ── Solicita datos del perfil ───> (Servidor a Servidor)
       │                                   │ <─ Devuelve email, nombre, sub ─ │
       │                                   │                                 │
  (8)  │                                   │ [Crea o vincula usuario User]   │
       │                                   │ [Genera par JWT propio (access/refresh)]
       │                                   │                                 │
  (9)  │ <── Redirige a /api/auth/social/jwt/ con par JWT propio ─────────── │
```

---

## 2. Detalle paso a paso: ¿Qué ocurre en el navegador y qué de servidor a servidor?

### En el Navegador (Front-channel / Canal Público):
1. **Paso 1 y 2 (Inicio):** El usuario navega a `/accounts/google/login/`. Nuestra aplicación genera una redirección hacia el servidor de autenticación de Google con los parámetros de la aplicación (`client_id`, `redirect_uri`, `scope`, `response_type=code`).
2. **Paso 3 (Consentimiento):** En el dominio seguro de Google, el usuario ingresa sus credenciales (si no tenía sesión abierta) y acepta compartir su perfil y dirección de email con TaskFlow.
3. **Paso 4 y 5 (Retorno del Código):** Google redirige al navegador de vuelta a nuestra `redirect_uri` (`http://127.0.0.1:8000/accounts/google/login/callback/`) pasando un `code` (código de autorización) temporal de un solo uso en la query string.

### De Servidor a Servidor (Back-channel / Canal Seguro):
4. **Paso 6 (Intercambio de Credenciales):** Nuestro servidor Django (a través de `django-allauth`) toma ese código y hace una petición POST directa contra los servidores de Google. En esta petición envía el `code`, junto con el `client_id` y el **`client_secret`** (el secreto privado que nunca se expone al navegador).
5. **Paso 7 (Obtención de Identidad):** Google valida el código y el secreto, y devuelve un token de acceso a su API. Con él, Django solicita la información del usuario (email, id único de Google, nombre).
6. **Paso 8 y 9 (Emisión de JWT propio):**
   - Django verifica si ya existe un `User` con esa cuenta social; si no, lo crea automáticamente.
   - Establece la sesión y redirige a nuestra vista `SocialLoginJWTView` (`/api/auth/social/jwt/`), la cual genera un token JWT (`access` y `refresh`) propio de TaskFlow.
   - De este modo, a partir de ese momento el cliente interactúa con los endpoints protegidos de nuestra API usando el header estándar `Authorization: Bearer <access_token>`.
