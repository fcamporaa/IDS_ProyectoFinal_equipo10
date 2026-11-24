# Plan de implementación — ABM de Servicios del Candy Bar (Backoffice Admin)

- **Tarea:** Tarea 3 — ABM de Servicios Adicionales (Candy Bar).
- **Rama de trabajo:** `feature/admin-abm-peliculas` (misma rama de la Tarea 1; si el equipo prefiere, crear `feature/admin-abm-servicios` desde `develop`).
- **Módulo:** Backoffice de Administración.
- **Estado:** Planificado. **No se modificó ningún archivo de código todavía.**
- **Documento base:** `docs/hito-3-tareas.md`, `docs/Proyecto integrador IDS 2026.pdf`, `docs/swagger.yaml`, `AGENTS.md`, `docs/tasks/01_plan_ABM+OMDb.md` (esquema de referencia).

---

## 1. Objetivo

Permitir que un usuario con rol `ADMINISTRADOR` gestione el catálogo de servicios adicionales del Candy Bar desde el backoffice:

1. Listar **todos** los servicios registrados, activos e inactivos.
2. Dar de alta un servicio (nombre, tipo COMIDA/BEBIDA, precio).
3. Editar los datos de un servicio existente.
4. Dar de baja lógica un servicio y reactivarlo.
5. Todo mediante **SSR con Flask + Jinja2**, sin `fetch()`, `axios`, AJAX ni WebSockets.

### Fuera de alcance de esta tarea

- ABM de películas (Tarea 1).
- Programar funciones en salas (Tarea 2).
- Validador QR (Tarea 4).
- Rediseño del navbar (Tarea 11). Solo se agregará un acceso directo desde el dashboard.
- Modificar el esquema de la base de datos ni agregar dependencias.
- Integración con API externa (no aplica; los datos son locales).

---

## 2. Requisitos y trazabilidad

| Requisito | Fuente | Cómo se cumple |
| :--- | :--- | :--- |
| Vista solo para administradores en `/admin/servicios` | `docs/hito-3-tareas.md` | Blueprint protegido con `@admin_required` en todas las rutas. |
| Listado completo de servicios | Hito 3 + enunciado | Nuevo endpoint `GET /servicios/admin` que devuelve activos e inactivos. |
| Alta de servicio que guarde en MySQL | Hito 3 | `POST /admin/servicios` → `POST /servicios` del backend. |
| Refrescar la tabla de servicios | Hito 3 | Redirección `POST/Redirect/GET` al listado. |
| Dar de baja un servicio | Hito 3 | `POST /admin/servicios/<id>/eliminar` → `DELETE /servicios/<id>` (baja lógica). |
| ABM completo (alta, baja, modificación) | Título “ABM” + enunciado | Edición con `PUT /servicios/<id>` y reactivación con `PUT {"activo": true}`. |
| Prohibido `fetch`/AJAX | Enunciado + AGENTS.md | Toda comunicación pasa por `frontend/services/` con `requests`. |
| Prohibido ORM y clases | AGENTS.md | Funciones procedurales y SQL parametrizado en repositorios. |
| No agregar dependencias | AGENTS.md | `requests`, Flask, PyMySQL y Jinja2 ya están instalados. |

---

## 3. Auditoría del estado actual

### 3.1 Backend disponible

| Endpoint | Auth | Comportamiento actual | Reutilización |
| :--- | :--- | :--- | :--- |
| `GET /servicios` | Pública | Devuelve **solo servicios activos** (`activo = 1`). | Catálogo de compra (cliente). **No sirve para el listado ABM.** |
| `GET /servicios/<id>` | N/A (no existe) | — | No hay endpoint de detalle individual; `PUT` y `DELETE` validan existencia internamente. |
| `POST /servicios` | Admin | Crea servicio con nombre, tipo, precio. Valida duplicados por nombre. | Alta. |
| `PUT /servicios/<id>` | Admin | Actualiza nombre, tipo, precio, activo. | Edición y reactivación. |
| `DELETE /servicios/<id>` | Admin | Baja lógica: `activo = 0`. Seguro repetir (idempotente). | Baja. |

### 3.2 Brechas detectadas

| # | Brecha | Impacto | Decisión propuesta |
| :-: | :--- | :--- | :--- |
| **S1** | No existe endpoint para listar **todos** los servicios (activos e inactivos). `GET /servicios` filtra `activo = 1`. | Una alta nueva o un servicio inactivo no aparecerían en la tabla del backoffice; no se podrían editar ni reactivar. | Crear `GET /servicios/admin` (Solo Admin) que devuelve todos los servicios con su estado. |
| **S2** | No existe endpoint de detalle individual `GET /servicios/<id>`. | Para el formulario de edición no hay lectura directa; hay que inferirla del listado admin. | Reutilizar `GET /servicios/admin` y buscar el servicio por `id_servicio` en el frontend. No crear endpoint nuevo (evita duplicar lógica). |
| **S3** | No existe frontend backoffice para servicios. | No hay vista para operar el ABM desde el navegador. | Crear la vista completa (Fases 3 a 5), igual que en la Tarea 1. |
| **S4** | El dashboard no tiene acceso a la gestión de servicios. | El admin no llega a la vista fácilmente. | Agregar botón “Gestionar servicios” en `backoffice/dashboard.html`. |

### 3.3 Activos reutilizables del proyecto

| Activo | Uso en esta tarea |
| :--- | :--- |
| `frontend/services/api_client.py` → `consultar_backend()` | Único cliente HTTP; GET/POST/PUT/DELETE con Bearer y errores 502. |
| `frontend/utils/auth.py` → `@admin_required` | Protección de todas las rutas web del backoffice. |
| `frontend/utils/errores.py` → `extraer_mensaje_error()` | Mensajes de error legibles para `flash()`. |
| `frontend/templates/layout.html` | Estructura base, navbar y mensajes flash. |
| `frontend/templates/components/button.html` | Botones y enlaces con variantes `primary`/`secondary`/`danger`. |
| `frontend/templates/components/campo_formulario.html` | Inputs con `valor`, `tipo`, `minimo`, `maximo`, `obligatorio`, `maxlength`. |
| `frontend/templates/backoffice/dashboard.html` | Patrón visual de cabecera, secciones y tablas del backoffice. |
| `frontend/static/css/tokens.css` | Colores, radios, sombras y transiciones del design system. |
| `frontend/static/css/pages/dashboard.css` | Patrón de página, header y alertas. |
| `frontend/static/css/components/tabla_dashboard.css` | Patrón de tabla responsive con scroll horizontal. |
| `backend/src/constants.py` | `TIPOS_SERVICIO`, códigos HTTP, utilidades de error. |
| `backend/src/utils.py` | `validar_admin`, `construir_error_api`, `crear_error_http`, `error_validacion`, `error_no_encontrado`. |
| `backend/src/repositories/servicios_repository.py` | `ejecutar_consulta`, `ejecutar_mutacion` y consultas existentes. |

---

## 4. Decisiones de diseño

### D1 — SSR puro, sin llamadas desde el navegador

El navegador solo envía formularios `GET`/`POST` al frontend Flask. El frontend llama al backend con `requests` a través de `consultar_backend()`. El JavaScript solo manipula el DOM (abrir/cerrar modales, confirmar bajas).

### D2 — Endpoint admin separado para el listado completo

`GET /servicios` es un contrato público del catálogo de compra (solo activos). Cambiar su comportamiento según el token rompería la experiencia de cliente. Se agrega `GET /servicios/admin`.

### D3 — No se crea endpoint de detalle individual

El backend ya no tiene `GET /servicios/<id>`. Para editar, el frontend lee el listado admin y busca el servicio por `id_servicio` en memoria. Evita duplicar una ruta que solo filtra una fila.

### D4 — Edición completa reutilizando `PUT /servicios/<id>`

El endpoint `PUT` ya acepta nombre, tipo, precio y activo. La UI permite editar todo y reactivar con `{"activo": true}`.

### D5 — Baja y reactivación mediante `POST`

Las acciones de estado se envían por formularios `POST` a rutas del frontend; el backend sigue usando `DELETE` (baja lógica) y `PUT` (reactivación).

### D6 — Sin cambios de esquema ni dependencias

La tabla `servicios` cubre todos los campos. No se agregan paquetes a `requirements.txt`.

### D7 — Regla anti-duplicación y modularidad (obligatoria, D10 de la Tarea 1)

Todo lo que se escriba debe ser modular y reutilizable:

| Responsabilidad | Único lugar autorizado | Prohibido |
| :--- | :--- | :--- |
| Llamadas HTTP al backend | `frontend/services/*.py` vía `consultar_backend()` | `requests` directo en rutas o templates |
| Autorización de vistas | `@admin_required` | Chequeos manuales de rol en cada ruta |
| Mensajes de error | `extraer_mensaje_error()` | `respuesta["errors"][0]` repetido |
| SQL | `repositories/*.py` con `%s` | SQL en services/routes |
| Constantes de servicio | `backend/src/constants.py` | strings `"COMIDA"`, `"BEBIDA"` dispersos |
| Inputs de formulario | `components/campo_formulario.html` (extendido) | nuevo componente de input por página |
| Botones | `components/button.html` | HTML de botón suelto |
| Modal de confirmación | `components/modal_confirmacion.html` + `modal.css` | un modal distinto por acción |
| Tokens de diseño | `static/css/tokens.css` | hex hardcodeados en CSS de página |
| Apertura/cierre de modales | helpers únicos en `admin_servicios.js` | listeners duplicados por fila |

**Regla:** si algo se usa una sola vez y no es conceptualmente compartido, se deja en su lugar. No se crean parámetros ni helpers “por si acaso”. Cada abstracción debe tener al menos dos usos reales.

---

## 5. Contrato de datos

### 5.1 Servicio (respuesta del backend)

```json
{
  "id_servicio": 1,
  "nombre": "Combo Popcorn Grande + Gaseosa",
  "tipo": "COMIDA",
  "precio": 8500.00,
  "activo": true
}
```

### 5.2 Payload de alta (`POST /servicios`)

```json
{
  "nombre": "Combo Popcorn Grande + Gaseosa",
  "tipo": "COMIDA",
  "precio": 8500.00
}
```

`activo` se setea a `1` automáticamente por el validador; el frontend no lo envía en alta.

### 5.3 Payload de edición (`PUT /servicios/<id>`)

Campos opcionales (al menos uno):

```json
{
  "nombre": "Combo Popcorn Grande + Gaseosa",
  "tipo": "COMIDA",
  "precio": 9000.00,
  "activo": true
}
```

### 5.4 Reglas de validación (reutilizar validadores existentes)

| Campo | Regla |
| :--- | :--- |
| `nombre` | 1 a 50 caracteres, requerido, único. |
| `tipo` | `COMIDA` o `BEBIDA` (constante `TIPOS_SERVICIO`). |
| `precio` | decimal positivo, máximo 2 decimales, hasta `99999999.99`. |
| `activo` | booleano (solo en edición). |
| Duplicado | Backend bloquea nombre repetido (400). |

---

## 6. Plan paso a paso por archivo

### Fase 0 — Prerrequisitos de entorno (sin código)

> Estado en esta máquina: ✅ resuelto. `backend/.env` ya tiene `OMDB_API_KEY` (verificada) y `frontend/.env` ya tiene `SECRET_KEY` de 64 caracteres. MySQL responde en `localhost:3306`.

1. Confirmar que `backend/.env` tenga `OMDB_API_KEY` válida (ya cargada en esta máquina).
2. Confirmar que `frontend/.env` tenga `SECRET_KEY` de al menos 32 caracteres (ya cargada en esta máquina).
3. Confirmar que MySQL esté levantado en el puerto de `backend/.env` (`DB_PORT`, en esta máquina `3306`).
4. Confirmar credenciales de prueba del seed: `admin@cineparadiso.com` / `Admin1234!` y `cliente@cineparadiso.com` / `Cliente1234!`.
5. Confirmar rama:
   ```bash
   git branch --show-current
   # feature/admin-abm-peliculas (o feature/admin-abm-servicios desde develop)
   ```

### Fase 1 — Backend: cerrar brecha S1

#### 1.1 `backend/src/constants.py`

- No se requieren constantes nuevas (`TIPOS_SERVICIO` ya existe). Si se desea, agregar `HTTP_OK`, `HTTP_CREADO`, etc. ya existen.

#### 1.2 `backend/src/repositories/servicios_repository.py`

- Agregar `SQL_SELECCIONAR_SERVICIOS_ADMIN`:
  - Selecciona `id_servicio, nombre, tipo, precio, activo`.
  - `ORDER BY activo DESC, nombre`.
- Agregar `obtener_servicios_admin_db() -> list[dict]` usando `ejecutar_consulta`.
- No duplicar SQL existente ni modificar `obtener_servicios_activos_db`.

#### 1.3 `backend/src/services/servicios_services.py`

- Agregar `listar_servicios_admin() -> list[dict]`:
  - Llama a `obtener_servicios_admin_db()`.
  - Reutiliza `_serializar_servicio()` para convertir `activo` a booleano y `precio` de `Decimal` a `float`.
- No modificar `listar_servicios()` (solo activos).

#### 1.4 `backend/src/routes/servicios_routes.py`

- Importar `listar_servicios_admin`.
- Agregar `GET /servicios/admin`:
  - `validar_admin(request.headers.get("Authorization"))`.
  - `jsonify(listar_servicios_admin()), 200`.
- Declarar antes de `/servicios/<int:id>` si existiera (no hay conflicto real porque `admin` es segmento estático).

#### 1.5 `docs/swagger.yaml`

- Documentar `GET /servicios/admin`:
  - `security: BearerAuth`, respuestas `200`, `401`, `403`.
  - Respuesta: array de `Servicio`.
- Actualizar `operationId` y descripciones.

### Fase 2 — Frontend: servicios y utilidades

#### 2.1 `frontend/services/admin_servicios_service.py` (nuevo)

Funciones HTTP, todas con `token`:

```python
listar_servicios_admin(token)           # GET /servicios/admin
crear_servicio(token, datos)            # POST /servicios
actualizar_servicio(token, id_servicio, datos)  # PUT /servicios/<id>
dar_de_baja_servicio(token, id_servicio)        # DELETE /servicios/<id>
reactivar_servicio(token, id_servicio)            # PUT /servicios/<id> {"activo": True}
```

Todas devuelven `(cuerpo, status)`. Sin reglas de negocio ni transformación.

#### 2.2 `frontend/utils/peliculas.py`

- No tocar (pertenece a la Tarea 1). No crear utilidades nuevas a menos que se repitan.

### Fase 3 — Frontend: rutas web

#### 3.1 `frontend/routes/admin_servicios_routes.py` (nuevo)

```python
admin_servicios_bp = Blueprint(
    "admin_servicios", __name__, url_prefix="/admin/servicios"
)
```

Todas las rutas con `@admin_required`.

| Ruta | Método | Función | Responsabilidad |
| :--- | :--- | :--- | :--- |
| `/admin/servicios` | GET | `index()` | Listar servicios (todos, activos e inactivos). |
| `/admin/servicios` | POST | `crear()` | Leer formulario, armar payload, llamar `POST /servicios`. |
| `/admin/servicios/<int:id>/editar` | GET | `editar()` | Buscar servicio en el listado admin; renderizar formulario precargado. |
| `/admin/servicios/<int:id>/editar` | POST | `actualizar()` | Leer formulario, llamar `PUT /servicios/<id>`. |
| `/admin/servicios/<int:id>/eliminar` | POST | `eliminar()` | Llamar `DELETE /servicios/<id>`. |
| `/admin/servicios/<int:id>/reactivar` | POST | `reactivar()` | Llamar `PUT /servicios/<id>` con `{"activo": true}`. |

Lógica de `index()`:

1. Leer `session["access_token"]`.
2. Llamar `listar_servicios_admin(token)`. Si `401/403`, limpiar sesión y redirigir a login. Si `!= 200`, `flash` y `servicios = []`.
3. Pasar a la plantilla: `servicios`, `error_backend`.

Lógica de `editar(id_servicio)`:

1. Llamar `listar_servicios_admin(token)` (o cachear del index si viene del mismo flujo).
2. Buscar `servicio = next((s for s in servicios if s["id_servicio"] == id_servicio), None)`.
3. Si no existe, `flash` y redirigir al listado.
4. Armar `borrador` con `nombre`, `tipo`, `precio`, `activo`.
5. Renderizar con `modo_formulario="editar"` y `accion_formulario=url_for("admin_servicios.actualizar", id_servicio=...)`.

Helpers internos:

- `_leer_formulario(form)`:
  - `nombre` (text, requerido, max 50).
  - `tipo` (select: COMIDA / BEBIDA).
  - `precio` (number, min 0.01, step 0.01, max 99999999.99).
  - `activo` (checkbox solo en edición: `form.get("activo") == "on"`).
- `_redirigir_sesion_expirada()`: limpia sesión, `flash`, redirect a login.
- `_renderizar_pagina(servicios, error_backend, borrador=None, abrir_formulario=False, modo_formulario="crear", accion_formulario=None)`: centraliza carga y render.

Manejo de errores:

- `401/403`: sesión expirada.
- `400`: `flash(extraer_mensaje_error(respuesta))` y re-render con `borrador` del formulario.
- `404`: servicio no encontrado.
- `409`: duplicado.
- `502`: backend no disponible.

#### 3.2 `frontend/app.py`

- Importar `admin_servicios_bp`.
- Registrar con `app.register_blueprint(admin_servicios_bp)`.

### Fase 4 — Frontend: componentes y plantilla

#### 4.1 `frontend/templates/backoffice/servicios.html` (nuevo)

Estructura:

1. `{% extends 'layout.html' %}`.
2. `{% block title %}Gestión de servicios | Cinema Paradiso{% endblock %}`.
3. `{% block extra_css %}` con `css/pages/admin_servicios.css`.
4. Cabecera: eyebrow “Backoffice”, título “Gestión de servicios (Candy Bar)”, subtítulo, enlaces “Volver al dashboard” y “Volver a la cartelera”.
5. Alerta de error de carga (`error_backend`).
6. Botón “Nuevo servicio” que abre el formulario en modo crear (`abrir_formulario=True`).
7. Formulario (mismo componente que alta/edición):
   - Campos: `nombre`, `tipo` (select COMIDA/BEBIDA), `precio`.
   - Si edición: checkbox `activo`.
   - Botón submit: “Guardar servicio” / “Guardar cambios”.
   - Enlace cancelar al listado.
8. Tabla de servicios:
   - Columnas: Nombre, Tipo, Precio, Estado, Acciones.
   - Estado: badge “Activo” / “Inactivo”.
   - Acciones: “Editar”, “Dar de baja” (modal de confirmación), “Reactivar”.
   - Tabla con scroll horizontal en móviles.
9. `{% block extra_scripts %}` con `js/admin_servicios.js`.

#### 4.2 `frontend/templates/components/formulario_servicio.html` (nuevo)

Componente parametrizado reutilizado por alta y edición:

- Recibe: `modo_formulario`, `accion_formulario`, `borrador`, `abrir_formulario`.
- Contrato de `borrador` (siempre con estas claves): `nombre`, `tipo`, `precio`, `activo`.
- Campos:
  - `nombre` (text, required, maxlength 50).
  - `tipo` (select con opciones `COMIDA`, `BEBIDA`; `checked`/`selected` si coincide con `borrador.tipo`).
  - `precio` (number, min 0.01, step 0.01, required).
  - Si `modo_formulario == "editar"`: checkbox `activo`.
  - Botón submit + enlace cancelar.
- Reutilizar `components/campo_formulario.html` (extender con `opciones` para select si no existe; si no, renderizar select a mano dentro del componente) y `components/button.html`.

> Nota: `campo_formulario.html` actual soporta `tipo`, `minimo`, `valor`, `obligatorio`. Para `<select>` con opciones de tipo, se agrega parámetro opcional `opciones` (lista de `{valor, etiqueta}`) o se renderiza el select dentro del mismo componente. Se verifica que `client/checkout.html` siga igual.

#### 4.3 `frontend/templates/components/modal_confirmacion.html` (nuevo)

Componente genérico reutilizable para confirmar bajas:

- Parámetros: `id_modal`, `titulo`, `mensaje`, `accion`, `texto_confirmar`, `texto_cancelar`.
- Formulario `POST` con `action="{{ accion }}"`.
- Botones “Cancelar” y “Confirmar baja”.
- `role="dialog"`, `aria-modal="true"`, `aria-labelledby`.
- Se abre desde JS con `data-modal-open`.

#### 4.4 `frontend/templates/backoffice/dashboard.html`

- Agregar botón “Gestionar servicios” en el header que apunte a `url_for('admin_servicios.index')`.
- No modificar la lógica del dashboard.

### Fase 5 — Frontend: CSS y JavaScript

#### 5.1 `frontend/static/css/pages/admin_servicios.css` (nuevo)

Tokens de `tokens.css`:

- `.admin-servicios` — padding y layout.
- `.admin-servicios__header` — patrón de `dashboard-page__header`.
- `.admin-servicios__form` — grilla del formulario.
- `.admin-servicios__table-wrapper` — `overflow-x: auto`.
- `.admin-servicios__badge` — variantes activo/inactivo.
- Media queries: `< 900px` formulario una columna; `< 640px` tabla con scroll.

#### 5.2 `frontend/static/css/components/modal.css` (nuevo)

- `.modal`, `.modal__backdrop`, `.modal__dialog`, `.modal__header`, `.modal__body`, `.modal__actions`, `.modal__close`.
- Estado `.modal[hidden]` / `.modal--abierto`.
- `body.modal-abierto { overflow: hidden; }`.
- Reutilizable por la Tarea 1 (películas) y Tarea 4 (QR).

#### 5.3 `frontend/static/css/style.css`

- Agregar `@import "components/modal.css";` en la sección de componentes.

#### 5.4 `frontend/static/js/admin_servicios.js` (nuevo)

Solo DOM, sin red:

- `DOMContentLoaded`.
- Abrir/cerrar modales: `[data-modal-open]`, `[data-modal-close]`, click en backdrop, tecla `Escape`.
- Confirmación de baja: interceptar submit de formularios con `data-confirmar-baja`, abrir modal, enviar formulario real al confirmar.
- Auto-apertura: si `data-abrir-formulario="true"`, hacer scroll y foco al formulario.
- **No usar `fetch`, `XMLHttpRequest`, `axios`, promesas de red ni WebSockets.**

### Fase 6 — Documentación y cierre

- Actualizar `docs/swagger.yaml` (Fase 1.5).
- No modificar `requirements.txt`.
- No modificar `init_db.sql` ni `seed_data.sql`.

---

## 7. Flujos funcionales esperados

### 7.1 Listado

1. Admin entra a `/admin/servicios`.
2. `@admin_required` valida sesión y rol.
3. El frontend llama `GET /servicios/admin` con token.
4. Se renderiza la tabla con todos los servicios, activos e inactivos.
5. Si el backend falla, flash y tabla vacía sin romper la página.

### 7.2 Alta

1. Admin hace clic en “Nuevo servicio”.
2. Completa `nombre`, `tipo`, `precio`.
3. `POST /admin/servicios` arma el payload.
4. Frontend llama `POST /servicios` con `Authorization: Bearer`.
5. Backend valida, inserta en MySQL.
6. `201` → flash de éxito y redirect al listado.
7. `400` → flash y re-render del formulario con los datos cargados.

### 7.3 Edición

1. Admin hace clic en “Editar”.
2. `GET /admin/servicios/<id>/editar`.
3. Frontend busca el servicio en el listado admin y precarga el formulario.
4. `POST` a la misma ruta → `PUT /servicios/<id>`.
5. `200` → flash de éxito y redirect.

### 7.4 Baja y reactivación

- Baja: “Dar de baja” abre modal de confirmación → `POST /admin/servicios/<id>/eliminar` → `DELETE /servicios/<id>` → `activo = 0`.
- Reactivación: “Reactivar” → `POST /admin/servicios/<id>/reactivar` → `PUT /servicios/<id> {"activo": true}`.

---

## 8. Seguridad y validaciones

| Capa | Medida |
| :--- | :--- |
| Frontend | `@admin_required` en las 6 rutas. |
| Frontend | Token de `session["access_token"]`; nunca en HTML. |
| Frontend | Acciones de baja/reactivación por `POST`, no `GET`. |
| Frontend | `flash()` con `extraer_mensaje_error()`; sin trazas internas. |
| Backend | `validar_admin()` en listado admin, alta, edición y baja. |
| Backend | SQL en repositorios, parametrizado con `%s` / `%(nombre)s`. |
| Backend | Validadores reutilizan `src/utils.py` y `src/constants.py`. |
| Datos | Nombre único (backend lo valida y devuelve 400). |
| Datos | Precio decimal positivo con 2 decimales. |
| CSRF | `SameSite=Lax` y formularios `POST` cubren el caso básico. |

---

## 9. Casos borde y manejo

| Caso | Comportamiento |
| :--- | :--- |
| Servicio ya inactivo al dar de baja | Backend devuelve `true` (idempotente); flash “ya estaba inactivo” o “dado de baja”. |
| Nombre duplicado | Backend 400 con “Ya existe un servicio con ese nombre.”; flash y re-render. |
| Servicio no encontrado en edición | Backend 404; flash y redirect al listado. |
| Precio negativo o con más de 2 decimales | Backend 400; flash y re-render. |
| Sesión expirada | Limpieza de sesión y redirect a login. |
| Backend caído | `consultar_backend` devuelve 502; flash y tabla vacía / formulario disponible. |
| Servicio con compras asociadas | La baja es lógica (`activo = 0`); las compras históricas conservan su referencia. |

---

## 10. Pruebas y QA

### 10.1 Verificación de sintaxis

```bash
python -m compileall backend/src frontend
```

### 10.2 Pruebas de backend con `curl`

1. Login admin y token:
   ```bash
   TOKEN=$(curl -s -X POST http://127.0.0.1:5000/auth/login \
     -H 'Content-Type: application/json' \
     -d '{"email":"admin@cineparadiso.com","contrasena":"Admin1234!"}' \
     | python -c 'import sys,json; print(json.load(sys.stdin)["token"])')
   ```
2. Listado admin (todos):
   ```bash
   curl -s http://127.0.0.1:5000/servicios/admin \
     -H "Authorization: Bearer $TOKEN"
   ```
3. Alta:
   ```bash
   curl -s -X POST http://127.0.0.1:5000/servicios \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"nombre":"Nachos con Queso","tipo":"COMIDA","precio":6400.00}'
   ```
4. Edición:
   ```bash
   curl -s -X PUT http://127.0.0.1:5000/servicios/<id> \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"precio":7000.00,"activo":true}'
   ```
5. Baja y reactivación:
   ```bash
   curl -s -X DELETE http://127.0.0.1:5000/servicios/<id> \
     -H "Authorization: Bearer $TOKEN"
   curl -s -X PUT http://127.0.0.1:5000/servicios/<id> \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"activo":true}'
   ```

### 10.3 Pruebas de permisos

- Sin token → `401`.
- Token de cliente → `403`.
- Token de admin → `200`/`201`.
- Web `/admin/servicios` sin sesión → redirect a login con flash.

### 10.4 Pruebas manuales de UI

- [ ] La vista carga sin errores.
- [ ] La tabla muestra activos e inactivos.
- [ ] Alta exitosa: aparece en la tabla y en MySQL.
- [ ] Alta duplicada: error claro y datos conservados.
- [ ] Edición exitosa: cambios reflejados en la tabla.
- [ ] Baja: modal confirma, servicio inactivo.
- [ ] Reactivación: vuelve a activo.
- [ ] Errores de backend/OMDb con `flash()`.
- [ ] Responsive en 360px, 768px, escritorio.
- [ ] No hay `fetch`, `axios`, `XMLHttpRequest` ni WebSockets en `admin_servicios.js`.
- [ ] `client/checkout.html` sigue renderizando igual tras extender `campo_formulario.html`.

### 10.5 Verificación en MySQL

```sql
SELECT id_servicio, nombre, tipo, precio, activo
FROM servicios
ORDER BY activo DESC, nombre;
```

---

## 11. Criterios de aceptación

- [ ] Existe la vista `/admin/servicios` y solo es accesible para `ADMINISTRADOR`.
- [ ] El listado incluye servicios activos e inactivos, con tipo y precio.
- [ ] Se puede dar de alta un servicio (nombre, tipo, precio).
- [ ] Se puede editar un servicio existente.
- [ ] Se puede dar de baja lógica y reactivar un servicio.
- [ ] Los errores del backend se muestran con `flash()`.
- [ ] No se usan `fetch`, `axios`, AJAX, WebSockets ni ORMs.
- [ ] No se agregaron dependencias.
- [ ] `docs/swagger.yaml` documenta el endpoint nuevo `GET /servicios/admin`.
- [ ] La vista es responsive y respeta el design system.
- [ ] No hay código duplicado evitable (regla D10): helpers únicos, un solo componente de input, un solo botón, un solo modal.
- [ ] `client/checkout.html` no se rompe al extender `campo_formulario.html`.

---

## 12. Riesgos y mitigaciones

| Riesgo | Probabilidad | Mitigación |
| :--- | :--- | :--- |
| Conflicto de rama con Tarea 1 | Media | Ambas tareas en la misma rama o crear rama separada desde `develop`; merges ordenados. |
| Servicio con compras históricas | Baja | Baja lógica no borra; compras conservan referencia. |
| Duplicados de nombre | Media | Backend bloquea; UI muestra error claro. |
| `frontend/.env` sin `SECRET_KEY` | Baja (ya resuelto en esta máquina) | Prerrequisito documentado. |
| Extender `campo_formulario.html` rompe checkout | Baja | Verificación explícita en QA 10.4. |

---

## 13. Orden de commits sugerido

1. `[Servicios][Backend] Agregar listado admin de servicios`
   - `servicios_repository.py`, `servicios_services.py`, `servicios_routes.py`, `docs/swagger.yaml`.
2. `[Servicios][Frontend] Agregar servicios HTTP y rutas web`
   - `frontend/services/admin_servicios_service.py`, `frontend/routes/admin_servicios_routes.py`, `frontend/app.py`.
3. `[Servicios][Frontend] Agregar vista, componentes y estilos`
   - `frontend/templates/backoffice/servicios.html`, `formulario_servicio.html`, `modal_confirmacion.html`, `admin_servicios.css`, `modal.css`, `style.css`, `admin_servicios.js`, enlace en dashboard.
4. `[Servicios][QA] Pruebas de backend y UI`
   - Ejecutar checklist de la sección 10.

---

## 14. Resumen de archivos

### Nuevos

```text
docs/tasks/02_plan_ABM+servicios.md
frontend/services/admin_servicios_service.py
frontend/routes/admin_servicios_routes.py
frontend/templates/backoffice/servicios.html
frontend/templates/components/formulario_servicio.html
frontend/templates/components/modal_confirmacion.html
frontend/static/css/pages/admin_servicios.css
frontend/static/css/components/modal.css
frontend/static/js/admin_servicios.js
```

### Modificados

```text
backend/src/repositories/servicios_repository.py
backend/src/services/servicios_services.py
backend/src/routes/servicios_routes.py
docs/swagger.yaml
frontend/app.py
frontend/templates/backoffice/dashboard.html
frontend/static/css/style.css
frontend/templates/components/campo_formulario.html   # solo si se agrega parámetro opcional para select
```

### Sin cambios

```text
backend/db/init_db.sql
backend/db/seed_data.sql
backend/requirements.txt
frontend/requirements.txt
frontend/templates/components/navbar.html   # se deja para Tarea 11
```

---

## 15. Decisiones confirmadas

1. **Listado admin: `GET /servicios/admin`** para todos los servicios (activos e inactivos). `GET /servicios` permanece solo-activos para el catálogo de compra.
2. **No se crea `GET /servicios/<id>`**: la edición lee el listado admin y busca por `id_servicio` en el frontend.
3. **Navbar sin cambios**: el acceso se agrega solo desde el dashboard; el navbar queda para la Tarea 11.
4. **Alcance: flujo completo integrado con frontend** (backend + rutas web + servicios HTTP + templates + componentes + CSS + JS).
5. **Regla D10 de anti-duplicación y modularidad** aplicada estrictamente (ver sección 4, punto D7).

---

## 16. Próximo paso

1. Revisar y aprobar este plan.
2. Implementar la Fase 1 (backend) con la skill `02-desarrollar-backend`.
3. Implementar las fases 2 a 5 (frontend) con la skill `03-desarrollar-frontend`.
4. Ejecutar el QA de la sección 10.
5. Auditar y commitear con la skill `04-revisar-y-commitear`, respetando el orden de commits de la sección 13.

**No se escribió código de la feature todavía. Solo se creó este documento de planificación.**