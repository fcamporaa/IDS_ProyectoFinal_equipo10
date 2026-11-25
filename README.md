# Cine Paradiso - Proyecto Integrador IDS 2026 (Equipo 10)

Sistema integral de gestión de cines, reserva de entradas y control de acceso desarrollado para la cátedra Lanzillotta (Introducción al Desarrollo de Software).

---

## 1. Arquitectura del Repositorio

El proyecto se divide en dos aplicaciones independientes en Python (Flask):
- **`/backend`**: API REST en Flask conectada a MySQL. Estructurada estrictamente en 4 capas (`routes` -> `validators` -> `services` -> `repositories`).
- **`/frontend`**: Servidor Web con renderizado del lado del servidor (SSR con Jinja2). Consume el backend mediante `requests` en Python.

---

## 2. Puesta en Marcha con Docker

### Paso 1: Configurar el archivo de entorno
```bash
cp .env.example .env
```

### Paso 2: Iniciar los servicios
```bash
docker compose up --build -d
```

Una vez levantados los contenedores:
- **Frontend (Web):** `http://localhost:5001`
- **Backend (API REST):** `http://localhost:5000`
- **Base de Datos (MySQL):** `localhost:3307`

---

## 3. Reinicio de Base de Datos (Init y Seeds)

Para reiniciar la base de datos a su estado inicial y recargar el esquema (`init_db.sql`) junto con los datos de prueba (`seed_data.sql`):

```bash
docker compose down -v
docker compose up -d
```

---

## 4. Puesta en Marcha Local (Manual)

### Paso 1: Base de Datos
```bash
cd backend
docker compose up -d
cd ..
```

### Paso 2: Backend
```bash
cp backend/.env.example backend/.env
cd backend
./init.sh
source .venv/bin/activate
python app.py
```

### Paso 3: Frontend
```bash
cp frontend/.env.example frontend/.env
cd frontend
./init.sh
source .venv/bin/activate
python app.py
```

---

## 5. Usuarios de Prueba

| Rol | Correo Electrónico | Contraseña |
| :--- | :--- | :--- |
| **ADMINISTRADOR** | `admin@cineparadiso.com` | `Admin1234!` |
| **CLIENTE** | `cliente@cineparadiso.com` | `Cliente1234!` |

---

## 6. Pruebas de API con Postman

En la carpeta [`docs/postman/`](docs/postman) se encuentran:
- `Cine_Paradiso_API.postman_collection.json`: Endpoints documentados y clasificados por módulo.
- `Cine_Paradiso_Local.postman_environment.json`: Entorno con variables locales y captura automática de tokens.
