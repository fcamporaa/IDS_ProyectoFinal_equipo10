# Guía de Integración Frontend - Backend (Arquitectura SSR)

> **Cine Paradiso - Cátedra Lanzillotta (IDS 2026)**  
> **Equipo 10**

Esta guía explica de forma clara y directa cómo conectar las pantallas del **Frontend** (Flask + Jinja2) con la **API REST del Backend** (Flask + MySQL) respetando las restricciones obligatorias de la cátedra: **prohibido el uso de `fetch()`, `axios` o AJAX en JavaScript**.

---

## 1. El Modelo Mental: ¿Cómo nos comunicamos sin `fetch()`?

En una arquitectura Server-Side Rendering (SSR), el navegador **nunca** llama directamente a la API en JavaScript.  
Toda la comunicación ocurre **de servidor a servidor** en Python:

```
[ Navegador Web ]                [ Servidor Frontend ]                [ Servidor Backend ]
 (HTML Puro / Links / Forms)        (Flask en puerto 5001)               (API REST en puerto 5000)
         |                                   |                                   |
         | --- 1. Clic en enlace (GET) ----> |                                   |
         |                                   | --- 2. requests.get() ----------> |
         |                                   | <--- 3. Responde JSON ----------- |
         |                                   | [ Inyecta datos en Template ]     |
         | <--- 4. Devuelve HTML armado ---- |                                   |
```

Hay exactamente dos escenarios:
1. **Lectura de Datos (`GET`)**: El usuario entra a una página (ej. la Cartelera o el Detalle de Película).
2. **Envío de Formularios (`POST`)**: El usuario envía datos (ej. Login, Registro o Confirmación de Compra).

---

## 2. La Herramienta Central: `consultar_backend()`

Todo el equipo debe usar la función unificada [`frontend/services/api_client.py`](../frontend/services/api_client.py). **No importes `requests` por tu cuenta**.

### Firma de la función:
```python
from services.api_client import consultar_backend

respuesta, status = consultar_backend(
    ruta="/peliculas",            # Ruta del endpoint (string)
    token=token,                  # Token JWT si el endpoint es protegido (opcional)
    params={"formato": "4D"},     # Query parameters para GET (opcional)
    metodo="GET",                 # "GET", "POST", "PUT" o "DELETE"
    datos={"campo": "valor"}      # Diccionario JSON para el body (opcional)
)
```

**Retorno:** Siempre devuelve una tupla `(cuerpo_respuesta, codigo_http_int)`. Si el backend está caído, devuelve `({"error": "..."}, 502)`.

---

## 3. Ejemplo Canónico 1: Mostrar Datos en una Vista (`GET`)

### Paso A: Crear el Servicio (`frontend/services/ejemplo_service.py`)
```python
from services.api_client import consultar_backend

def obtener_mis_datos():
    """Consulta el endpoint y retorna los datos o None si falló."""
    datos, status = consultar_backend("/peliculas", metodo="GET")
    if status == 200 and isinstance(datos, list):
        return datos
    return None
```

### Paso B: Llamarlo desde la Ruta Web (`frontend/routes/ejemplo_routes.py`)
```python
from flask import Blueprint, render_template
from services.ejemplo_service import obtener_mis_datos

ejemplo_bp = Blueprint("ejemplo", __name__)

@ejemplo_bp.route("/cartelera")
def ver_cartelera():
    # 1. Obtenemos los datos desde el servicio
    peliculas = obtener_mis_datos()
    
    # 2. Pasamos la variable al template Jinja2
    return render_template("cartelera.html", peliculas=peliculas)
```

### Paso C: Mostrarlo en el Template Jinja2 (`templates/cartelera.html`)
```html
{% extends 'layout.html' %}

{% block content %}
<h1>Películas en Cartelera</h1>

{% if peliculas %}
    <div class="grilla">
        {% for p in peliculas %}
            <article class="card">
                <h3>{{ p.titulo }}</h3>
                <p>Duración: {{ p.duracion_min }} min</p>
            </article>
        {% endfor %}
    </div>
{% else %}
    <p>No hay funciones disponibles en este momento.</p>
{% endif %}
{% endblock %}
```

---

## 4. Ejemplo Canónico 2: Procesar un Formulario y Guardar Sesión (`POST`)

### Paso A: El Formulario en Jinja2 (`templates/auth/login.html`)
```html
<form method="POST" action="{{ url_for('auth.login') }}">
    <!-- Token CSRF si aplica -->
    <label for="email">Correo Electrónico:</label>
    <input type="email" id="email" name="email" required>

    <label for="contrasena">Contraseña:</label>
    <input type="password" id="contrasena" name="contrasena" required>

    <button type="submit">Iniciar Sesión</button>
</form>
```

### Paso B: El Servicio (`frontend/services/auth_service.py`)
```python
from services.api_client import consultar_backend

def enviar_login_al_backend(email: str, contrasena: str):
    return consultar_backend(
        ruta="/auth/login",
        metodo="POST",
        datos={"email": email, "contrasena": contrasena}
    )
```

### Paso C: El Controlador Web (`frontend/routes/auth_routes.py`)
```python
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from services.auth_service import enviar_login_al_backend
from utils.errores import extraer_mensaje_error

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # 1. Leer los campos del formulario HTML
        email = request.form.get("email", "").strip()
        contrasena = request.form.get("contrasena", "").strip()

        # 2. Llamar al backend
        resultado, status = enviar_login_al_backend(email, contrasena)

        if status == 200 and "token" in resultado:
            # 3. Guardar el token y datos de usuario en la sesión de Flask
            session["access_token"] = resultado["token"]
            session["usuario"] = resultado["usuario"]
            flash(f"¡Bienvenido, {resultado['usuario']['nombre']}!", "exito")
            return redirect(url_for("home.index"))
        else:
            # 4. Extraer el mensaje oficial del backend o mensaje de red
            mensaje_error = extraer_mensaje_error(resultado, "Credenciales inválidas.")
            flash(mensaje_error, "error")

    return render_template("auth/login.html")
```

---

## 5. Cómo Usar Endpoints Protegidos (Token Bearer)

Cuando el usuario navega una ruta protegida (ej. ver sus compras o el dashboard de administrador):

```python
from flask import session, redirect, url_for, flash
from services.api_client import consultar_backend

def obtener_mis_compras():
    # 1. Recuperamos el token de la sesión activa
    token = session.get("access_token")
    if not token:
        return None

    # 2. Se lo pasamos a consultar_backend (lo enviará en el header Authorization)
    compras, status = consultar_backend("/compras/mis-compras", token=token, metodo="GET")
    if status == 200:
        return compras
    return []
```

---

## 6. Checklist de Buenas Prácticas para el Equipo

- [x] **Nunca uses `fetch()`, `axios` o llamadas AJAX** en archivos `.js`.
- [x] **Todo submit va a una ruta Flask `POST`** que luego redirige con `redirect(url_for(...))`.
- [x] **Usá siempre `consultar_backend()`** desde `frontend/services/` para no duplicar código de red.
- [x] **Manejá errores con `flash(mensaje, 'error')`** para que se muestren en el banner superior del layout.
- [x] **Los Blueprints siempre se registran** en `frontend/app.py` con `app.register_blueprint(...)`.

