# Cine Paradiso - Proyecto Integrador IDS 2026 (Equipo 10)

Sistema integral de gestión de cines, reserva de entradas y control de acceso desarrollado para la cátedra Lanzillotta (Introducción al Desarrollo de Software).

---

## 1. Arquitectura del Repositorio

El proyecto se divide en dos aplicaciones independientes en Python (Flask):
- **`/backend`**: API REST en Flask conectada a MySQL. Estructurada estrictamente en 4 capas (`routes` -> `validators` -> `services` -> `repositories`).
- **`/frontend`**: Servidor Web con renderizado del lado del servidor (SSR con Jinja2). Prohibido el uso de `fetch()`/AJAX; consume el backend mediante `requests` en Python.

---

## 2. Requisitos Previos

- **Python 3.10 a 3.12**
- **Docker** y **Docker Compose** (para la base de datos MySQL)

---

## 3. Puesta en Marcha Rápida

### Paso 1: Levantar la Base de Datos (MySQL)
La base de datos se inicializa automáticamente con el esquema de tablas y datos semilla de prueba:

```bash
cd backend
docker compose up -d
cd ..
```

*(El contenedor creará la base `proyecto_integrador` en el puerto `3307` con usuario `root` y contraseña `root`).*

### Paso 2: Levantar el Backend (API REST en :5000)
```bash
# 1. Asegurar el archivo de entorno
cp backend/.env.example backend/.env

# 2. Iniciar el servidor
cd backend
source .venv/bin/activate   # En Linux / Mac
python app.py
```
La API estará disponible en `http://127.0.0.1:5000`.

### Paso 3: Levantar el Frontend (Servidor Web en :5001)
En una nueva terminal:
```bash
# 1. Asegurar el archivo de entorno
cp frontend/.env.example frontend/.env

# 2. Iniciar el servidor
cd frontend
source .venv/bin/activate   # En Linux / Mac
python app.py
```
Abrí tu navegador en `http://127.0.0.1:5001`.

---

## 4. Credenciales de Prueba (Semillas de BD)

Al iniciar la base de datos con Docker, ya quedan disponibles los siguientes usuarios:

| Rol | Correo Electrónico | Contraseña |
| :--- | :--- | :--- |
| **ADMINISTRADOR** | `admin@cineparadiso.com` | `Admin1234!` |
| **CLIENTE** | `cliente@cineparadiso.com` | `Cliente1234!` |

---

## 5. Pruebas de API con Postman

En la carpeta [`docs/postman/`](docs/postman) disponés de:
- `Cine_Paradiso_API.postman_collection.json`: Los 28 endpoints documentados y organizados por módulo.
- `Cine_Paradiso_Local.postman_environment.json`: Entorno con variables locales y captura automática de tokens al iniciar sesión.

