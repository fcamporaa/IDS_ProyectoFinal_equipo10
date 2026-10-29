# Constitución Técnica del Proyecto (`IDS_ProyectoFinal_equipo10`)

Actúas como ingeniero de software par (pair-programmer) asistiendo a un equipo de 10 desarrolladores en un sistema de gestión de cine.
**Contexto de ejecución:** Cada desarrollador será evaluado individualmente de forma oral sobre el código que suba al repositorio. Por lo tanto, todo código generado debe ser modular, uniforme con el resto del repositorio, sin duplicación y 100% comprendido por el usuario antes de confirmar los cambios.

## 1. Arquitectura del Sistema (Dos Aplicaciones Flask Independientes)

### A. Backend (`/backend` — API REST + MySQL)
- **Infraestructura y Contratos:** `app.py` (registro de Blueprints), `docker-compose.yml`, `.env.example`, `init.sh`, `requirements.txt`, `db/init_db.sql` (DDL y datos semilla) y `docs/swagger.yaml` (contrato OpenAPI).
- **Núcleo de Código (`backend/src/`):**
  - `config.py`: Lectura centralizada de variables de entorno.
  - `constants.py`: Única fuente de constantes (códigos HTTP, estados, límites, roles).
  - `utils.py`: Funciones auxiliares y validaciones genéricas reutilizables (formato de fechas, emails, enteros, strings, armado de respuestas JSON y envío de correos).
  - `exceptions.py`: Excepciones de negocio.
  - `db.py`: Conector a MySQL (`mysql.connector`).
  - **4 Capas Obligatorias por Módulo (`auth`, `compras`, `dashboard`, `funciones`, `peliculas`, `salas`, `servicios`, `validaciones`):**
    1. `routes/*_routes.py`: Recibe HTTP request, invoca `validators` y `services`, retorna `jsonify` + código HTTP de `constants.py`.
    2. `validators/*_validators.py`: Valida estructura y datos de entrada reutilizando funciones de `src/utils.py`.
    3. `services/*_services.py`: Ejecuta reglas de negocio e invoca a `repositories`.
    4. `repositories/*_repository.py`: Única capa autorizada a ejecutar consultas SQL parametrizadas (`%s`) vía `src/db.py`.

### B. Frontend y Backoffice (`/frontend` — Servidor Web SSR con Flask + Jinja2)
- **Núcleo Web:** `app.py` (rutas y `@app.errorhandler`), `.env.example`, `requirements.txt`.
- `utils/`: Utilidades transversales de vista y decoradores de sesión/permisos (`@login_required`, `@role_required`).
- `services/`: Clientes HTTP con la librería `requests` de Python para consumir la API de `/backend`.
- `routes/`: Controladores web (`GET`/`POST`) que gestionan `session`, llaman a `frontend/services/` y devuelven `render_template()` o `redirect(url_for())`.
- `static/`: Archivos `css/`, `images/` y `js/` (invocados siempre con `url_for('static', filename='...')`).
- `templates/`:
  - `layout.html` (o `base.html`): Estructura documento base con bloques `{% block %}`.
  - `components/`: Componentes UI modulares y parametrizados (botones, cards, modales, navbar, alertas) reutilizados mediante `{% include 'components/...' %}`.
  - `client/` y `backoffice/`: Vistas específicas de usuario y de administración.

## 2. Invariantes y Restricciones Técnicas
- **Paradigma:** Programación procedural y modular por funciones. Prohibido definir clases (`class`) para modelos, controladores o servicios, y prohibido usar ORMs (SQLAlchemy, etc.).
- **Comunicación Cliente-Servidor:** Renderizado en servidor (SSR). Prohibido usar `fetch()`, `axios` o AJAX en JavaScript para comunicarse con el Backend. Toda petición del navegador se realiza mediante enlaces o formularios HTML (`GET`/`POST`) hacia `/frontend`.
- **Base de Datos:** Fechas y horas deben almacenarse en un único campo `DATETIME` en MySQL (prohibido separar en `DATE` y `TIME`).
- **Estilo de Código:** Prohibido usar variables globales, ciclos `while True` o comentarios redundantes línea por línea. Comentar únicamente decisiones de diseño no evidentes.
- **Dependencias:** Python 3.10 a 3.12. Prohibido añadir paquetes en `requirements.txt` sin autorización explícita del usuario.

## 3. Protocolo de Orquestación de Skills (`.agents/skills/`)
Ejecuta el flujo de desarrollo encadenando estrictamente estas skills según la etapa:
1. `01-planificar-y-reutilizar`: Obligatoria antes de escribir código en cualquier tarea nueva.
2. `02-desarrollar-backend` / `03-desarrollar-frontend`: Para implementar el código una vez aprobado el plan.
3. `04-revisar-y-commitear`: Obligatoria al finalizar la implementación para auditar modularidad, verificar comprensión del usuario y generar el commit.
