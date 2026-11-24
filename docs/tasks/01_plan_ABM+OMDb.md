# Plan de implementación — ABM de Películas + OMDb (Backoffice Admin)

- **Tarea:** Tarea 1 — ABM de Películas e Integración con OMDb.
- **Rama de trabajo:** `feature/admin-abm-peliculas` (creada desde `develop`).
- **Módulo:** Backoffice de Administración.
- **Estado:** Planificado. **No se modificó ningún archivo de código todavía.**
- **Documento base:** `docs/hito-3-tareas.md`, `docs/Proyecto integrador IDS 2026.pdf`, `docs/swagger.yaml`, `AGENTS.md`.

---

## 1. Objetivo

Permitir que un usuario con rol `ADMINISTRADOR` gestione el catálogo de películas desde el backoffice:

1. Listar todas las películas registradas, incluidas las dadas de baja.
2. Buscar películas en OMDb por título.
3. Seleccionar un resultado y **precargar** la ficha local con los datos de OMDb.
4. Dar de alta la película en MySQL junto con sus géneros.
5. Editar los datos de una película existente.
6. Dar de baja lógica una película y reactivarla.
7. Todo mediante **SSR con Flask + Jinja2**, sin `fetch()`, `axios`, AJAX ni WebSockets.

**Alcance de entrega:** este plan cubre el **flujo vertical completo**, no solo la lógica de la API. Cada acción tiene su cadena íntegra: formulario HTML → ruta del frontend → servicio HTTP → endpoint del backend → validadores → servicio → repositorio → MySQL/OMDb → respuesta → re-render o redirect con `flash()`. La Fase 1 agrega lo que falta en el backend y las Fases 2 a 5 construyen la vista del backoffice, sus componentes, estilos y JavaScript. Si un artefacto de frontend no existe, se crea respetando las convenciones de `03-desarrollar-frontend`.

**Qué significa “edición completa”:** poder modificar **todos** los campos editables de una película ya cargada —título, sinopsis, póster, tráiler, duración, clasificación, año, géneros y estado `activa`—, no solo darla de alta y de baja. Se implementa reutilizando `PUT /peliculas/<id>`, que ya existe.

### Fuera de alcance de esta tarea

- Programar funciones en salas (Tarea 2).
- ABM de servicios/Candy Bar (Tarea 3).
- Validador QR (Tarea 4).
- Rediseño completo del navbar (Tarea 11). Solo se agregará un acceso directo desde el dashboard.
- Modificar el esquema de la base de datos o agregar dependencias.

---

## 2. Requisitos y trazabilidad

| Requisito | Fuente | Cómo se cumple |
| :--- | :--- | :--- |
| Vista solo para administradores en `/admin/peliculas` | `docs/hito-3-tareas.md` | Blueprint protegido con `@admin_required` en todas las rutas. |
| Buscador conectado a OMDb | Enunciado + Hito 3 | Formulario `GET` SSR que llama al backend; el backend consulta OMDb. |
| Autocompletar título, póster, sinopsis, duración y clasificación | Hito 3 | Nuevo endpoint de detalle OMDb + formulario precargado en el servidor. |
| Formulario de alta que guarde en MySQL | Hito 3 | `POST /admin/peliculas` → `POST /peliculas` del backend. |
| Refrescar la tabla de películas | Hito 3 | Redirección `POST/Redirect/GET` al listado. |
| Dar de baja una película | Hito 3 | `POST /admin/peliculas/<id>/eliminar` → `DELETE /peliculas/<id>` (baja lógica). |
| ABM completo (alta, baja, modificación) | Título “ABM” + enunciado | Edición con `PUT /peliculas/<id>` y reactivación con `PUT {"activa": true}`. |
| Catálogo desde API gratuita | Enunciado | OMDb (`OMDB_API_KEY`, ya configurada en `constants.py`). |
| Prohibido `fetch`/AJAX | Enunciado + AGENTS.md | Toda comunicación pasa por `frontend/services/` con `requests`. |
| Prohibido ORM y clases | AGENTS.md | Se reutilizan funciones procedurales y SQL parametrizado en repositorios. |
| Fechas/horas en `DATETIME` | Enunciado | No se modifica el esquema; esta tarea no crea campos de fecha. |
| No agregar dependencias | AGENTS.md | `requests`, Flask, PyMySQL y Jinja2 ya están instalados. |

---

## 3. Auditoría del estado actual

### 3.1 Backend disponible

| Endpoint | Auth | Comportamiento actual | Reutilización |
| :--- | :--- | :--- | :--- |
| `GET /peliculas` | Pública | Devuelve **solo cartelera vigente**: películas `activa = 1` **con funciones** `PROGRAMADA`/`EN_CURSO` que aún no terminaron. | Cartelera pública. **No sirve para el listado ABM.** |
| `GET /peliculas/<id>` | Pública | Devuelve la película aunque esté inactiva, con `origen_api`, `id_api`, `activa`, `generos` y `funciones_vigentes`. | Precarga del formulario de edición. |
| `POST /peliculas` | Admin | Crea película y asocia géneros en una transacción. Valida duplicados por `origen_api` + `id_api`. | Alta. |
| `PUT /peliculas/<id>` | Admin | Actualiza campos editables y `activa`; puede reemplazar géneros. | Edición y reactivación. |
| `DELETE /peliculas/<id>` | Admin | Baja lógica: `activa = 0`. No borra físicamente. | Baja. |
| `GET /peliculas/externas/buscar?query=...` | Admin | Busca en OMDb y devuelve `id_api`, `titulo`, `anio`, `poster`, `origen`. | Resultados del buscador. |
| `GET /generos` | Pública | Lista los 8 géneros locales. | Checkboxes de géneros. |

### 3.2 Brechas detectadas

| # | Brecha | Impacto | Decisión propuesta |
| :-: | :--- | :--- | :--- |
| **G1** | No existe un endpoint para listar **todas** las películas (activas, inactivas y sin funciones). `GET /peliculas` es la cartelera pública. | Un alta nueva no aparecería en la tabla hasta programar una función; tampoco se podrían editar/dar de baja películas sin cartelera. | Crear `GET /peliculas/admin` (Solo Admin) que devuelve todas las películas con sus géneros. |
| **G2** | La búsqueda externa solo devuelve título, año y póster. OMDb no incluye sinopsis, duración ni clasificación en la búsqueda `s`. | No se puede cumplir el autocompletado completo de la ficha. | Crear `GET /peliculas/externas/<id_api>` (Solo Admin) que consulta OMDb con `i=<imdbID>&plot=full` y normaliza los campos. |
| **G3** | El Hito 3 documenta `?titulo=...`, pero el backend implementado espera `?query=...`. | Posible confusión al integrar o al probar con Postman/Swagger. | El frontend usará `query`. Además, aceptar `titulo` como alias en el validador para compatibilidad. |
| **G4** | `backend/.env` tiene `OMDB_API_KEY` vacía. | La búsqueda y el detalle externo devolverán error 500 de configuración. | Prerrequisito de entorno: completar la key desde omdbapi.com. No commitear el `.env`. |
| **G5** | `frontend/.env` no tiene `SECRET_KEY` y `frontend/app.py` aborta si falta. | El servidor web no arranca para probar la vista. | Prerrequisito local: agregar `SECRET_KEY` de al menos 32 caracteres. No es parte del código de la feature. |

### 3.3 Activos reutilizables del proyecto

| Activo | Uso en esta tarea |
| :--- | :--- |
| `frontend/services/api_client.py` → `consultar_backend()` | Único cliente HTTP; soporta GET/POST/PUT/DELETE, Bearer y errores 502. |
| `frontend/utils/auth.py` → `@admin_required` | Protección de todas las rutas web del backoffice. |
| `frontend/utils/errores.py` → `extraer_mensaje_error()` | Mensajes de error legibles para `flash()`. |
| `frontend/utils/peliculas.py` | Se ampliará con el mapeo de géneros OMDb → géneros locales. |
| `frontend/services/peliculas_service.py` | Se ampliará con `obtener_generos()` y reutilización del detalle. |
| `frontend/templates/layout.html` | Estructura base, navbar y mensajes flash. |
| `frontend/templates/components/button.html` | Botones y enlaces con variantes `primary`/`secondary`/`danger`. |
| `frontend/templates/components/campo_formulario.html` | Inputs con `valor`, `tipo`, `minimo` y `obligatorio`. |
| `frontend/templates/components/mensajes.html` | Alternativa de alertas; el layout ya muestra los flash. |
| `frontend/templates/backoffice/dashboard.html` | Patrón visual de cabecera, secciones y tablas del backoffice. |
| `frontend/static/css/tokens.css` | Colores, radios, sombras y transiciones del design system. |
| `frontend/static/css/pages/dashboard.css` | Patrón de página, header, alertas y responsive. |
| `frontend/static/css/components/tabla_dashboard.css` | Patrón de tabla responsive con scroll horizontal. |
| `backend/src/utils.py` | `validar_admin`, `validar_texto`, `crear_error_http`, `error_no_encontrado`, etc. |
| `backend/src/constants.py` | `OMDB_URL`, `OMDB_TIMEOUT_SEGUNDOS`, `OMDB_ERRORES_SIN_RESULTADOS`, `ORIGENES_API_PELICULAS`. |
| `backend/src/repositories/peliculas_repository.py` | `ejecutar_consulta`, `ejecutar_mutacion`, `ejecutar_transaccion` y consultas existentes. |

---

## 4. Decisiones de diseño

### D1 — SSR puro, sin llamadas desde el navegador

El navegador solo envía formularios `GET`/`POST` al frontend Flask. El frontend llama al backend con `requests` a través de `consultar_backend()`. El JavaScript nuevo solo manipulará el DOM (abrir/cerrar modales, previsualizar póster, confirmar bajas).

### D2 — Endpoint admin separado en lugar de modificar `GET /peliculas`

`GET /peliculas` es un contrato público de cartelera vigente. Cambiar su comportamiento según el token rompería la cartelera y mezclaría responsabilidades. Se agrega `GET /peliculas/admin`.

### D3 — Endpoint de detalle OMDb en el backend

La key de OMDb debe permanecer en el backend. Además, consultar el detalle desde el frontend duplicaría la integración externa y rompería la arquitectura. Se agrega `GET /peliculas/externas/<id_api>`.

### D4 — Precarga en servidor, no autocompletado con AJAX

Al seleccionar un resultado de OMDb, el navegador hace un `GET` normal a `/admin/peliculas?busqueda=...&id_api=...`. El servidor frontend consulta el detalle al backend y renderiza el formulario ya precargado. El JS solo abre el formulario y actualiza la vista previa del póster.

### D5 — Mapeo de géneros en frontend

OMDb devuelve géneros en inglés (`Action`, `Sci-Fi`, `Thriller`, etc.) y la BD local usa español (`Acción`, `Ciencia Ficción`, `Suspenso`, etc.). El mapeo se resuelve en `frontend/utils/peliculas.py`, sin tocar la API. Los géneros no reconocidos se muestran al administrador para que elija manualmente.

### D6 — Baja y reactivación mediante `POST`

Las acciones destructivas o de estado se envían por formularios `POST` a rutas del frontend, nunca por enlaces `GET`. El backend sigue usando `DELETE` (baja lógica) y `PUT` (reactivación).

### D7 — Edición reutilizando `GET /peliculas/<id>`

El formulario de edición se precarga con el detalle público, que ya devuelve también películas inactivas. No se necesita un endpoint nuevo para leer una película.

### D8 — Sin cambios de esquema ni dependencias

Las tablas `peliculas`, `generos` y `pelicula_generos` ya cubren todos los campos. No se agregan paquetes a `requirements.txt`.

### D9 — `query` como parámetro oficial y `titulo` como alias

El backend ya funciona con `query`. Para cumplir también la documentación del Hito 3, el validador aceptará `titulo` si `query` no viene. El frontend enviará siempre `query`.

### D10 — Regla anti-duplicación y modularidad (obligatoria)

Todo lo que se escriba en esta tarea tiene que ser **modular y reutilizable**. La regla operativa:

1. **Si algo se repite dos veces, se extrae.** Aplica a SQL, validaciones, payloads, helpers de ruta, bloques de template, reglas CSS y funciones de JS.
2. **Un solo lugar para cada responsabilidad:**

| Responsabilidad | Único lugar autorizado | Prohibido |
| :--- | :--- | :--- |
| Llamadas HTTP al backend | `frontend/services/*.py` vía `consultar_backend()` | `requests` directo en rutas o templates |
| Autorización de vistas | `@admin_required` | Chequeos manuales de rol en cada ruta |
| Mensajes de error | `extraer_mensaje_error()` | `respuesta["errors"][0]` repetido en cada ruta |
| SQL | `repositories/*.py` con `%s` | SQL en services/routes |
| Constantes y rutas de OMDb | `backend/src/constants.py` | strings `"N/A"`, `"movie"`, `"full"` dispersos |
| Formato de película (`activa` bool + `generos`) | `_formatear_peliculas()` | rearmar el mismo diccionario en cada servicio |
| Error 502 de OMDb | `_api_externa_no_disponible()` | crear otro error equivalente |
| Inputs de formulario | `components/campo_formulario.html` (extendido) | nuevo componente de input por página |
| Botones | `components/button.html` | HTML de botón suelto |
| Modal de confirmación | `components/modal_confirmacion.html` + `modal.css` | un modal distinto por acción |
| Tokens de diseño | `static/css/tokens.css` | hex hardcodeados en `admin_peliculas.css` |
| Apertura/cierre de modales y preview | helpers únicos en `admin_peliculas.js` | listeners duplicados por fila |

3. **Componentes parametrizados, no copias.** `formulario_pelicula.html` debe servir para alta y edición; `pelicula_externa_resultado.html` recibe un resultado y se itera. Si aparece un tercer caso de uso, se extiende el componente con un parámetro opcional, no se clona.
4. **Helpers de ruta únicos.** `_leer_formulario()`, `_renderizar_pagina()` y `_redirigir_sesion_expirada()` se definen una vez y los usan las 6 rutas.
5. **Sin duplicar componentes legacy.** El repo ya tiene pares duplicados (`button.html`/`boton.html`, `campo_formulario.html`/`form_field.html`). En esta tarea se usan **solo** `button.html` y `campo_formulario.html`; no se crea una tercera variante ni se tocan los legacy.
6. **Compatibilidad al extender.** Al agregar parámetros opcionales a `campo_formulario.html` (por ejemplo `maxlength`, `lista`, `tipo="textarea"`), la inclusión actual de `client/checkout.html` debe seguir renderizando igual. Se verifica antes de cerrar la tarea.
7. **Reutilizar sin sobre-abstraer.** Si un bloque se usa una sola vez y no es conceptualmente compartido, se deja en su lugar. No se crean parámetros ni helpers “por si acaso”: cada abstracción debe tener al menos dos usos reales dentro de esta tarea o ser un componente transversal del proyecto.

---

## 5. Contrato de datos

### 5.1 Detalle externo OMDb propuesto

`GET /peliculas/externas/<id_api>` responderá `200` con:

```json
{
  "id_api": "tt15239678",
  "titulo": "Dune: Part Two",
  "anio_estreno": 2024,
  "poster_url": "https://m.media-amazon.com/images/M/....jpg",
  "sinopsis": "Paul Atreides unites with Chani and the Fremen...",
  "duracion_min": 166,
  "clasificacion": "PG-13",
  "generos": ["Action", "Adventure", "Drama", "Sci-Fi"],
  "origen_api": "OMDB"
}
```

Reglas de normalización:

| Campo OMDb | Campo local | Regla |
| :--- | :--- | :--- |
| `Title` | `titulo` | Texto directo. |
| `Year` | `anio_estreno` | Se toman los primeros 4 dígitos; si no son numéricos → `null`. |
| `Poster` | `poster_url` | `"N/A"` → `null`. |
| `Plot` | `sinopsis` | `"N/A"` → `null`. Se solicita `plot=full`. |
| `Runtime` | `duracion_min` | Se extrae el primer número (`"166 min"` → `166`); `"N/A"` → `null`. |
| `Rated` | `clasificacion` | `"N/A"` → `null`. Se muestra tal cual (ej. `PG-13`, `R`) y el admin puede ajustarla a `ATP`, `+13`, `+16`, `+18`. |
| `Genre` | `generos` (solo sugerencia) | Se separa por comas y se usa para mapear ids locales. |
| `imdbID` | `id_api` | Identificador externo. |
| — | `origen_api` | `"OMDB"`. |
| — | `trailer_url` | OMDb no lo provee; queda `null` y es editable manualmente. |

### 5.2 Payload de alta (`POST /peliculas`)

```json
{
  "titulo": "Dune: Part Two",
  "sinopsis": "Paul Atreides unites with Chani...",
  "poster_url": "https://m.media-amazon.com/images/M/....jpg",
  "trailer_url": null,
  "duracion_min": 166,
  "clasificacion": "PG-13",
  "anio_estreno": 2024,
  "origen_api": "OMDB",
  "id_api": "tt15239678",
  "generos_ids": [1, 2, 3, 4]
}
```

Si el alta es manual (sin OMDb), se envía `origen_api = "CUSTOM"` e `id_api = null`.

### 5.3 Payload de edición (`PUT /peliculas/<id>`)

Solo campos editables:

```json
{
  "titulo": "Dune: Parte Dos",
  "sinopsis": "...",
  "poster_url": "...",
  "trailer_url": "...",
  "duracion_min": 166,
  "clasificacion": "+13",
  "anio_estreno": 2024,
  "activa": true,
  "generos_ids": [2, 3]
}
```

`origen_api` e `id_api` no se envían en la edición: el validador actual los ignora y no deben modificarse desde la UI.

### 5.4 Mapeo de géneros OMDb → géneros locales

| OMDb | Local |
| :--- | :--- |
| `Action` | `Acción` |
| `Adventure` | `Aventura` |
| `Animation` | `Animación` |
| `Comedy` | `Comedia` |
| `Drama` | `Drama` |
| `Horror` | `Terror` |
| `Sci-Fi`, `Science Fiction` | `Ciencia Ficción` |
| `Thriller`, `Mystery`, `Crime` | `Suspenso` |

Los géneros no mapeados (`Fantasy`, `Romance`, `War`, etc.) se listan como “géneros sin equivalente local” y el admin decide si agrega alguno de los 8 disponibles.

---

## 6. Plan paso a paso por archivo

### Fase 0 — Prerrequisitos de entorno (sin código)

> **Estado en esta máquina: ✅ resuelto.** `backend/.env` ya tiene `OMDB_API_KEY` (verificada contra OMDb) y `frontend/.env` ya tiene `SECRET_KEY` de 64 caracteres. MySQL responde en `localhost:3306`. Se dejan las instrucciones para cualquier otro entorno.

1. Verificar que `backend/.env` tenga una `OMDB_API_KEY` válida. Si está vacía:
   - Pedir una key gratuita (1.000 consultas/día) en <https://www.omdbapi.com/apikey.aspx> con un email; llega un link de activación y después la key.
   - Completar `OMDB_API_KEY=...` en `backend/.env`.
   - La key **no** se comparte por chat ni se commitea; `.env` ya está en `.gitignore`.
   - Smoke test sin exponer la key:
     ```bash
     cd backend
     .venv/bin/python -c "from src.services.peliculas_services import buscar_peliculas_externas; print(len(buscar_peliculas_externas({'query':'Dune'})))"
     # esperado: 10
     ```
2. Verificar que `frontend/.env` tenga `SECRET_KEY` de al menos 32 caracteres. No es un servicio externo: es la clave con la que Flask firma la cookie de sesión. Se genera localmente:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
   - Agregar `SECRET_KEY=<valor generado>` a `frontend/.env`.
   - Cada integrante puede usar una distinta en su máquina; si se cambia, se invalidan las sesiones abiertas.
3. Confirmar que MySQL esté levantado en el puerto que declara `backend/.env` (`DB_PORT`). En esta máquina es `localhost:3306`; si se usa el `docker-compose.yml` del repo, el puerto publicado es `3307` y hay que ajustar `DB_PORT` en `.env`. Verificar con:
   ```bash
   cd backend
   .venv/bin/python -c "from src.db import obtener_conexion; obtener_conexion().close(); print('mysql ok')"
   ```
4. Confirmar las credenciales de prueba del seed: `admin@cineparadiso.com` / `Admin1234!` (admin) y `cliente@cineparadiso.com` / `Cliente1234!` (cliente).
5. Confirmar rama:
   ```bash
   git branch --show-current
   # feature/admin-abm-peliculas
   ```

### Fase 1 — Backend: cerrar brechas G1, G2 y G3

#### 1.1 `backend/src/constants.py`

- Agregar constantes para evitar strings mágicos:
  - `OMDB_VALOR_NO_DISPONIBLE = "N/A"`
  - `OMDB_TIPO_PELICULA = "movie"`
  - `OMDB_TRAMA_COMPLETA = "full"`
- No modificar `OMDB_URL`, `OMDB_TIMEOUT_SEGUNDOS` ni `OMDB_ERRORES_SIN_RESULTADOS`.

#### 1.2 `backend/src/repositories/peliculas_repository.py`

- Agregar `SQL_SELECCIONAR_PELICULAS_ADMIN`:
  - Selecciona `id_pelicula, origen_api, id_api, titulo, sinopsis, poster_url, trailer_url, duracion_min, clasificacion, anio_estreno, activa`.
  - `ORDER BY activa DESC, titulo`.
- Agregar `obtener_peliculas_admin_db() -> list[dict]` usando `ejecutar_consulta`.
- No duplicar SQL existente ni modificar las consultas de cartelera.

#### 1.3 `backend/src/validators/peliculas_validators.py`

- Agregar `validar_id_externo(id_api: str) -> str`:
  - Reutiliza `validar_texto(id_api, "id_api", 50)`.
- Modificar `validar_busqueda_externa(args)`:
  - Leer `query`; si no viene, leer `titulo`.
  - Mantener el máximo de 100 caracteres y el error si ambos están vacíos.

#### 1.4 `backend/src/services/peliculas_services.py`

- Agregar helpers privados:
  - `_texto_omdb(valor)` → devuelve `None` para `None`, `"N/A"` o texto vacío.
  - `_entero_omdb(valor)` → extrae el primer número de un texto (`"166 min"`, `"2024–"`); si no hay, `None`.
  - `_formatear_detalle_externo(item)` → normaliza el JSON de OMDb al contrato de la sección 5.1.
- Agregar `listar_peliculas_admin() -> list[dict]`:
  - Llama a `obtener_peliculas_admin_db()`.
  - Reutiliza `_formatear_peliculas()` para convertir `activa` a booleano y agregar `generos`.
- Agregar `obtener_pelicula_externa(id_api: str) -> dict`:
  - Si `OMDB_API_KEY` está vacía → error 500 de configuración (mismo criterio que `buscar_peliculas_externas`).
  - Consulta `OMDB_URL` con `apikey`, `i=id_api`, `plot=full`.
  - Captura `requests.RequestException` y `ValueError` → error 502.
  - Si `Response != "True"`:
    - `"Movie not found!"` → `error_no_encontrado(...)` (404).
    - Otro error → error 502.
  - Devuelve `_formatear_detalle_externo(datos)`.
- Mantener `buscar_peliculas_externas()` sin cambios funcionales; solo reutilizar `OMDB_TIPO_PELICULA` si se extrae la constante.

#### 1.5 `backend/src/routes/peliculas_routes.py`

- Importar `listar_peliculas_admin`, `obtener_pelicula_externa`, `validar_id_externo`.
- Agregar `GET /peliculas/admin`:
  - `validar_admin(request.headers.get("Authorization"))`.
  - `jsonify(listar_peliculas_admin()), 200`.
- Agregar `GET /peliculas/externas/<string:id_api>`:
  - `validar_admin(...)`.
  - `validar_id_externo(id_api)`.
  - `jsonify(obtener_pelicula_externa(...)), 200`.
- No hay conflicto de rutas: Werkzeug prioriza los segmentos estáticos sobre los converters, así que `/peliculas/externas/buscar` gana sobre `/peliculas/externas/<string:id_api>`, y `<int:id>` nunca matchea `externas`. Aun así, declarar `buscar` antes de `<string:id_api>` deja el archivo más legible.

#### 1.6 `docs/swagger.yaml`

- Documentar `GET /peliculas/admin`:
  - `security: BearerAuth`, respuestas `200`, `401`, `403`.
  - Respuesta: array de `PeliculaDetalle`.
- Documentar `GET /peliculas/externas/{id_api}`:
  - Parámetro de path `id_api`.
  - Respuestas `200`, `400`, `401`, `403`, `404`, `502`.
  - Nuevo schema `PeliculaExternaDetalle` con los campos de la sección 5.1.
- Documentar el alias `titulo` en `/peliculas/externas/buscar` (opcional, marcado como compatibilidad).
- Actualizar `operationId` y descripciones para que el contrato quede claro.

### Fase 2 — Frontend: servicios y utilidades

#### 2.1 `frontend/services/peliculas_service.py`

- Agregar `obtener_generos()`:
  - `consultar_backend("/generos", metodo="GET")`.
  - Devuelve la tupla `(datos, status)` para que la ruta decida.
- **No** reutilizar `obtener_detalle_pelicula(id_pelicula)` para la edición: descarta el código HTTP y la ruta necesita distinguir `404` (película inexistente) de `502` (backend caído). Para eso se agrega `obtener_pelicula(token, id_pelicula)` en el servicio admin (sección 2.2).
- No duplicar `_adaptar_pelicula_para_vista()`; es exclusivo de la cartelera pública.

#### 2.2 `frontend/services/admin_peliculas_service.py` (nuevo)

Funciones HTTP, todas con `token`:

```python
listar_peliculas_admin(token)                  # GET /peliculas/admin
obtener_pelicula(token, id_pelicula)           # GET /peliculas/<id>
buscar_peliculas_externas(token, titulo)       # GET /peliculas/externas/buscar?query=...
obtener_pelicula_externa(token, id_api)        # GET /peliculas/externas/<id_api>
crear_pelicula(token, datos)                   # POST /peliculas
actualizar_pelicula(token, id_pelicula, datos) # PUT /peliculas/<id>
dar_de_baja_pelicula(token, id_pelicula)       # DELETE /peliculas/<id>
reactivar_pelicula(token, id_pelicula)         # PUT /peliculas/<id> {"activa": True}
```

Todas devuelven `(cuerpo, status)`. No implementan reglas de negocio ni transforman datos.

#### 2.3 `frontend/utils/peliculas.py`

- Agregar:
  - `MAPEO_GENEROS_OMDB`: diccionario normalizado (sin acentos, minúsculas) → nombre local.
  - `mapear_generos_externos(nombres_externos, generos_disponibles) -> tuple[list[int], list[str]]`:
    - Devuelve `(ids_sugeridos, nombres_sin_equivalente)`.
    - No falla si un género no existe.
- Mantener `agrupar_funciones()` intacto.

### Fase 3 — Frontend: rutas web

#### 3.1 `frontend/routes/admin_peliculas_routes.py` (nuevo)

```python
admin_peliculas_bp = Blueprint(
    "admin_peliculas", __name__, url_prefix="/admin/peliculas"
)
```

Todas las rutas llevan `@admin_required`.

| Ruta | Método | Función | Responsabilidad |
| :--- | :--- | :--- | :--- |
| `/admin/peliculas` | GET | `index()` | Listar películas, géneros, ejecutar búsqueda OMDb y preparar el borrador seleccionado. |
| `/admin/peliculas` | POST | `crear()` | Leer formulario, armar payload y llamar `POST /peliculas`. |
| `/admin/peliculas/<int:id>/editar` | GET | `editar()` | Cargar detalle y géneros; renderizar formulario precargado. |
| `/admin/peliculas/<int:id>/editar` | POST | `actualizar()` | Leer formulario y llamar `PUT /peliculas/<id>`. |
| `/admin/peliculas/<int:id>/eliminar` | POST | `eliminar()` | Llamar `DELETE /peliculas/<id>` y volver al listado. |
| `/admin/peliculas/<int:id>/reactivar` | POST | `reactivar()` | Llamar `PUT /peliculas/<id>` con `{"activa": true}`. |

Lógica de `index()`:

1. Leer `session["access_token"]`.
2. Obtener películas admin; si `401/403`, limpiar sesión, `flash` y redirigir a login. Si `!= 200`, `flash` y continuar con `peliculas = []`.
3. Obtener géneros; si `!= 200`, `flash` y continuar con `generos = []` (el formulario avisa que no se pudieron cargar).
4. Leer `busqueda = request.args.get("busqueda", "").strip()`.
5. Si hay `busqueda`, llamar `buscar_peliculas_externas(token, busqueda)`. Si falla (`!= 200`), `flash(extraer_mensaje_error(...))` y `resultados_externos = []`; la página sigue mostrando el formulario manual.
6. Leer `id_api = request.args.get("id_api", "").strip()`.
7. Si hay `id_api`, llamar `obtener_pelicula_externa(token, id_api)`. Si `200`, mapear géneros con `mapear_generos_externos(detalle["generos"], generos)`, armar `borrador` y usar `abrir_formulario=True`. Si falla, `flash` y dejar `borrador` vacío (`abrir_formulario=False`).
8. Pasar a la plantilla:
   - `peliculas`, `generos`, `busqueda`, `resultados_externos`, `borrador`, `abrir_formulario`, `modo_formulario="crear"`, `accion_formulario`, `error_backend`.

Lógica de `editar()`:

1. Llamar `obtener_pelicula(token, id_pelicula)` (devuelve `(detalle, status)`).
2. Si `status == 404`, `flash("Película no encontrada.")` y redirigir al listado. Si `status in (401, 403)`, `_redirigir_sesion_expirada()`. Si `status != 200`, `flash` y redirigir al listado.
3. `obtener_generos()`.
4. Armar `borrador` con los campos del detalle y `generos_ids = [g["id_genero"] for g in detalle["generos"]]`; `generos_no_mapeados = []`.
5. `_renderizar_pagina(borrador=..., abrir_formulario=True, modo_formulario="editar", accion_formulario=url_for("admin_peliculas.actualizar", id_pelicula=id_pelicula), busqueda="")`. La búsqueda OMDb queda fuera de esta pantalla; los resultados se muestran solo en `index()`.

Lógica de `crear()`:

1. `datos = _leer_formulario(request.form)`. Si lanza `ValueError` por duración/año, `flash` y re-render con `borrador` armado desde el formulario.
2. `crear_pelicula(token, datos)`.
3. `201` → `flash("Película creada correctamente.")` y `redirect(url_for("admin_peliculas.index"))`.
4. `401/403` → `_redirigir_sesion_expirada()`.
5. `400`, `409` o `502` → `flash(extraer_mensaje_error(respuesta))` y re-render con `borrador` desde el formulario y `abrir_formulario=True`.
6. Cualquier otro estado → `flash` genérico y re-render.

Lógica de `actualizar(id_pelicula)`:

1. `datos = _leer_formulario(request.form)`; siempre incluye `activa`.
2. `actualizar_pelicula(token, id_pelicula, datos)`.
3. `200` → `flash("Cambios guardados.")` y redirect al listado.
4. `404` → `flash("Película no encontrada.")` y redirect al listado.
5. `400`/`502` → `flash` y re-render del formulario de edición con el `borrador` enviado.

Lógica de `eliminar(id_pelicula)` y `reactivar(id_pelicula)`:

1. `dar_de_baja_pelicula(token, id)` / `reactivar_pelicula(token, id)`.
2. `200` → `flash` de éxito y redirect al listado.
3. `404` → `flash("Película no encontrada.")` y redirect.
4. `401/403` → `_redirigir_sesion_expirada()`.
5. Cualquier otro error → `flash(extraer_mensaje_error(...))` y redirect al listado (no se re-renderiza nada porque son acciones de una sola vía).

Helpers internos de la ruta:

- `_leer_formulario(form)`:
  - Textos: `titulo`, `sinopsis`, `poster_url`, `trailer_url`, `clasificacion`.
  - Enteros: `duracion_min`, `anio_estreno` (convertir; si falla, `flash` y no llamar al backend).
  - `origen_api`: `OMDB` si hay `id_api`, si no `CUSTOM`.
  - `generos_ids`: `form.getlist("generos_ids")` convertidos a `int`.
  - `activa`: `form.get("activa") == "on"` en edición.
- `_redirigir_sesion_expirada()`:
  - Limpia `access_token` y `usuario`, `flash` y redirige a `auth.login`.
- `_renderizar_pagina(...)` (obligatorio, no opcional):
  - Centraliza la carga de películas/géneros y el `render_template()` para no duplicar código entre `index()`, `crear()` y `editar()`.
  - Recibe `borrador`, `abrir_formulario`, `modo_formulario`, `accion_formulario` y `busqueda`; el resto del contexto lo resuelve adentro.

Manejo de errores:

- `401/403`: sesión expirada → limpiar y redirigir a login.
- `400`: `flash(extraer_mensaje_error(respuesta))` y volver al formulario.
- `404`: película no encontrada → `flash` y listado.
- `409`: duplicado/conflicto → `flash` con el mensaje del backend.
- `502`: backend/OMDb no disponible → `flash` y mostrar formulario manual.
- Errores locales de conversión (duración/año): `flash` antes de llamar al backend.

#### 3.2 `frontend/app.py`

- Importar `admin_peliculas_bp`.
- Registrar con `app.register_blueprint(admin_peliculas_bp)`.
- No modificar el context processor ni la configuración de sesión.

### Fase 4 — Frontend: componentes y plantilla

#### 4.1 `frontend/templates/backoffice/peliculas.html` (nuevo)

Estructura:

1. `{% extends 'layout.html' %}`.
2. `{% block title %}Gestión de películas | Cinema Paradiso{% endblock %}`.
3. `{% block extra_css %}` con `url_for('static', filename='css/pages/admin_peliculas.css')`.
4. Cabecera:
   - Eyebrow “Backoffice”.
   - Título “Gestión de películas”.
   - Subtítulo explicativo.
   - Enlaces: “Volver al dashboard” y “Volver a la cartelera”.
5. Alerta de error de carga (`{% if error_backend %}`), con el mismo patrón visual que `dashboard.html` (`.dashboard-alert` o su equivalente en `admin_peliculas.css`). Los errores de acción se muestran por `flash()` en el layout.
6. Buscador OMDb:
   - `<form method="get" action="{{ url_for('admin_peliculas.index') }}">`.
   - Input `name="busqueda"` con `value="{{ busqueda }}"`.
   - Botón “Buscar en OMDb”.
   - Botón “Limpiar” si hay búsqueda.
7. Resultados externos:
   - Si `resultados_externos`: grilla de `components/pelicula_externa_resultado.html`.
   - Cada resultado muestra póster, título, año, `id_api` y botón “Usar esta ficha”.
   - El botón es un enlace `GET` a `url_for('admin_peliculas.index', busqueda=busqueda, id_api=resultado.id_api)`.
   - Si la película ya existe (`id_api` coincide con la tabla), mostrar badge “Ya cargada” y enlace a editar/reactivar.
   - Si no hay resultados: mensaje vacío.
8. Formulario:
   - Incluir `components/formulario_pelicula.html` con:
     - `modo_formulario` (`crear`/`editar`).
     - `accion_formulario`.
     - `borrador`.
     - `generos`.
     - `abrir_formulario`.
9. Tabla de películas:
   - Título “Películas registradas”.
   - Columnas: Póster, Título, Año, Duración, Clasificación, Géneros, Origen, Estado, Acciones.
   - Póster con `loading="lazy"` y placeholder si no hay URL.
   - Estado: badge “Activa” / “Inactiva”.
   - Acciones:
     - “Editar” → `url_for('admin_peliculas.editar', id_pelicula=...)`.
     - “Dar de baja” → formulario `POST` a `url_for('admin_peliculas.eliminar', ...)` con `data-confirmar-baja`.
     - “Reactivar” → formulario `POST` a `url_for('admin_peliculas.reactivar', ...)`.
   - Tabla dentro de `.admin-peliculas__table-wrapper` con scroll horizontal.
10. `{% block extra_scripts %}` con `url_for('static', filename='js/admin_peliculas.js')`.

#### 4.2 `frontend/templates/components/formulario_pelicula.html` (nuevo)

Componente parametrizado reutilizado por alta y edición:

- Recibe: `modo_formulario`, `accion_formulario`, `borrador`, `generos`, `abrir_formulario`.
- Contrato de `borrador` (siempre con estas claves; la ruta garantiza que existan, aunque sea con `None`/`[]`, para que el mismo componente sirva en alta vacía, alta precargada desde OMDb, alta fallida y edición):
  `titulo`, `sinopsis`, `poster_url`, `trailer_url`, `duracion_min`, `clasificacion`, `anio_estreno`, `origen_api`, `id_api`, `generos_ids`, `generos_no_mapeados`, `activa`.
- Campos:
  - Hidden `origen_api` y `id_api` solo en modo creación.
  - `titulo` (text, required, maxlength 250).
  - `anio_estreno` (number, min 1888, max año actual + 5).
  - `duracion_min` (number, min 1, required).
  - `clasificacion` (text, maxlength 20, con `list` de sugerencias `ATP`, `+13`, `+16`, `+18`, `PG`, `PG-13`, `R`).
  - `poster_url` (url, maxlength 1000) + vista previa.
  - `sinopsis` (textarea, maxlength 10000).
  - `trailer_url` (url, maxlength 1000).
  - Géneros: checkboxes `name="generos_ids"` con `value="{{ genero.id_genero }}"` y `checked` si está en `borrador.generos_ids`.
  - Si `modo_formulario == "editar"`: checkbox `activa`.
  - Botón submit: “Guardar película” / “Guardar cambios”.
  - Enlace cancelar al listado.
- Mostrar `borrador.generos_no_mapeados` si existe, como aviso.
- **Reutilización obligatoria (D10):**
  - Inputs `text`, `number`, `url` y `textarea` → `components/campo_formulario.html`, **extendido** con tres parámetros opcionales: `maxlength`, `lista` (id de `datalist`) y `tipo='textarea'` (renderiza `<textarea>` con el contenido en vez de `<input>`). Sin parámetros nuevos, el HTML actual no cambia (checkout sigue igual).
  - Botones → `components/button.html` con `variante`.
  - No se crea ningún componente de input adicional ni se usa `form_field.html`/`boton.html`.

#### 4.3 `frontend/templates/components/pelicula_externa_resultado.html` (nuevo)

- Recibe `resultado`, `busqueda`, `ya_existe`, `id_pelicula_existente`.
- Renderiza tarjeta con póster, título, año, `id_api`.
- Si `ya_existe`: badge y enlace a editar o reactivar.
- Si no: enlace “Usar esta ficha” al `index` con `id_api`.

#### 4.4 `frontend/templates/components/modal_confirmacion.html` (nuevo)

Componente genérico reutilizable para confirmar bajas:

- Parámetros: `id_modal`, `titulo`, `mensaje`, `accion`, `texto_confirmar`, `texto_cancelar`.
- Formulario `POST` con `action="{{ accion }}"`.
- Botones “Cancelar” y “Confirmar baja”.
- `role="dialog"`, `aria-modal="true"`, `aria-labelledby`.
- Se abrirá desde JS con `data-modal-open`.

#### 4.5 `frontend/templates/backoffice/dashboard.html`

- Agregar un botón “Gestionar películas” en el header que apunte a `url_for('admin_peliculas.index')`.
- No modificar la lógica del dashboard.
- Dejar el enlace del navbar para la Tarea 11 y evitar conflictos de rama.

### Fase 5 — Frontend: CSS y JavaScript

#### 5.1 `frontend/static/css/pages/admin_peliculas.css` (nuevo)

Usar exclusivamente tokens de `tokens.css`:

- `.admin-peliculas` — padding y layout de página.
- `.admin-peliculas__header` — patrón de `dashboard-page__header`.
- `.admin-peliculas__search` — formulario de búsqueda en una fila.
- `.admin-peliculas__results` — grilla responsive de resultados.
- `.admin-peliculas__result-card` — tarjeta con póster 2:3.
- `.admin-peliculas__form` — grilla de dos columnas para el formulario.
- `.admin-peliculas__genres` — checkboxes en grilla.
- `.admin-peliculas__poster-preview` — vista previa del póster.
- `.admin-peliculas__table-wrapper` — `overflow-x: auto`.
- `.admin-peliculas__badge` — variantes activa/inactiva.
- `.admin-peliculas__actions` — acciones de fila.
- Media queries:
  - `< 900px`: formulario a una columna.
  - `< 640px`: resultados a una columna, tabla con scroll, botones full width.
- Respetar foco visible y contraste.

#### 5.2 `frontend/static/css/components/modal.css` (nuevo)

- `.modal`, `.modal__backdrop`, `.modal__dialog`, `.modal__header`, `.modal__body`, `.modal__actions`, `.modal__close`.
- Estado `.modal[hidden]` / `.modal--abierto`.
- `body.modal-abierto { overflow: hidden; }`.
- Reutilizable por las tareas 3 y 4.

#### 5.3 `frontend/static/css/style.css`

- Agregar `@import "components/modal.css";` en la sección de componentes.
- No mover ni renombrar imports existentes.

#### 5.4 `frontend/static/js/admin_peliculas.js` (nuevo)

Solo manipulación del DOM, sin red:

- `DOMContentLoaded`.
- Abrir/cerrar modales:
  - `[data-modal-open]` → quita `hidden`, agrega clase, enfoca el diálogo.
  - `[data-modal-close]`, click en backdrop y tecla `Escape` → cierra.
- Confirmación de baja:
  - Interceptar submit de formularios con `data-confirmar-baja`.
  - Abrir modal, mostrar título de la película y enviar el formulario real al confirmar.
  - Si el usuario cancela, no se envía.
- Vista previa del póster:
  - Escuchar `input` del campo `poster_url`.
  - Actualizar `src` de la imagen; si está vacío, mostrar placeholder.
- Auto-apertura:
  - Si el formulario tiene `data-abrir-formulario="true"` (selección OMDb o edición), hacer scroll y foco al formulario.
- No usar `fetch`, `XMLHttpRequest`, `axios`, promesas de red ni WebSockets.

### Fase 6 — Documentación y cierre

- Actualizar `docs/swagger.yaml` (Fase 1.6).
- Opcional: agregar al final de `docs/hito-3-tareas.md` una nota de que la Tarea 1 requirió dos endpoints complementarios (`/peliculas/admin` y `/peliculas/externas/{id_api}`).
- No modificar `requirements.txt`.
- No modificar `init_db.sql` ni `seed_data.sql`.

---

## 7. Flujos funcionales esperados

### 7.1 Listado

1. Admin entra a `/admin/peliculas`.
2. `@admin_required` valida sesión y rol.
3. El frontend llama `GET /peliculas/admin` y `GET /generos`.
4. Se renderiza la tabla con todas las películas, activas e inactivas.
5. Si el backend falla, se muestra un flash y una tabla vacía sin romper la página.

### 7.2 Búsqueda OMDb

1. Admin escribe “Dune” y envía el formulario `GET`.
2. URL: `/admin/peliculas?busqueda=Dune`.
3. El frontend llama `GET /peliculas/externas/buscar?query=Dune` con token.
4. Se muestran hasta 10 resultados con póster, título y año.
5. Si no hay resultados, mensaje “No se encontraron películas”.
6. Si OMDb falla, flash con el error y se mantiene el formulario manual.

### 7.3 Selección y precarga

1. Admin hace clic en “Usar esta ficha”.
2. URL: `/admin/peliculas?busqueda=Dune&id_api=tt15239678`.
3. El frontend llama `GET /peliculas/externas/tt15239678`.
4. Normaliza duración, año, sinopsis, póster y clasificación.
5. Mapea géneros OMDb a ids locales.
6. Renderiza el formulario precargado y lo abre.
7. El admin revisa y corrige lo que haga falta.

### 7.4 Alta

1. Admin completa campos obligatorios (`titulo`, `duracion_min`, al menos un género).
2. `POST /admin/peliculas` arma el payload.
3. Frontend llama `POST /peliculas` con `Authorization: Bearer`.
4. Backend valida, inserta película y géneros en una transacción.
5. `201` → flash de éxito y redirect al listado (`POST/Redirect/GET`).
6. `400` → flash con `errores.extraer_mensaje_error(respuesta)` y **re-render del mismo listado** con el formulario abierto y `borrador` armado a partir de `request.form`, para no perder lo que el admin ya había cargado. No se redirige.
7. `502` (backend u OMDb caído) → mismo criterio que `400`, con un flash que aclara que el servicio externo no está disponible.

El mismo criterio de re-render con `borrador` se aplica en `editar()` cuando el `PUT` devuelve `400`.

### 7.5 Edición

1. Admin hace clic en “Editar”.
2. `GET /admin/peliculas/<id>/editar`.
3. Frontend llama `GET /peliculas/<id>` y `GET /generos`.
4. Se precargan todos los campos y los géneros seleccionados.
5. `POST` a la misma ruta → `PUT /peliculas/<id>`.
6. `200` → flash de éxito y redirect.

### 7.6 Baja y reactivación

- Baja:
  1. “Dar de baja” abre el modal de confirmación.
  2. Confirmar → `POST /admin/peliculas/<id>/eliminar`.
  3. Frontend llama `DELETE /peliculas/<id>`.
  4. Backend marca `activa = 0`.
  5. Redirect con flash “Película dada de baja”.
- Reactivación:
  1. “Reactivar” → `POST /admin/peliculas/<id>/reactivar`.
  2. Frontend llama `PUT /peliculas/<id>` con `{"activa": true}`.
  3. Redirect con flash “Película reactivada”.

---

## 8. Seguridad y validaciones

| Capa | Medida |
| :--- | :--- |
| Frontend | `@admin_required` en las 6 rutas; sin excepciones. |
| Frontend | Token tomado de `session["access_token"]`; nunca se envía al navegador en HTML. |
| Frontend | Acciones de baja/reactivación por `POST`, no por `GET`. |
| Frontend | `flash()` con `extraer_mensaje_error()`; no se muestran trazas ni detalles internos. |
| Backend | `validar_admin()` en el listado admin, búsqueda externa, detalle externo, alta, edición y baja. |
| Backend | SQL exclusivamente en repositorios y parametrizado con `%s`. |
| Backend | Validadores reutilizan `src/utils.py`; no se duplican reglas. |
| Backend | `OMDB_API_KEY` solo en el servidor; nunca en el frontend. |
| Datos | Límites de longitud alineados con la BD: título 250, sinopsis 10000, URLs 1000, clasificación 20. |
| Datos | `duracion_min` entero positivo; `anio_estreno` entre 1888 y año actual + 5. |
| Datos | Al menos un género por película. |
| CSRF | El proyecto no tiene CSRF general. `SameSite=Lax` y formularios `POST` cubren el caso básico. Se deja como mejora futura si el equipo lo decide. |

---

## 9. Casos borde y manejo

| Caso | Comportamiento esperado |
| :--- | :--- |
| OMDb devuelve `Poster: "N/A"` | `poster_url = null`; la tabla y el formulario muestran placeholder “Sin póster”. |
| OMDb devuelve `Runtime: "N/A"` | `duracion_min = null`; el campo queda vacío y es obligatorio completarlo. |
| OMDb devuelve `Rated: "N/A"` | `clasificacion = null`; el admin la completa. |
| OMDb devuelve `Plot: "N/A"` | `sinopsis = null`; el admin la completa. |
| OMDb devuelve géneros sin equivalente local | Se listan como “sin equivalente” y el admin elige entre los 8 géneros disponibles. |
| OMDb no encuentra la película | Backend 404 o lista vacía según el caso; flash informativo. |
| `OMDB_API_KEY` vacía | Backend 500 de configuración; flash “Falta configurar OMDB_API_KEY”. El formulario manual sigue disponible. |
| OMDb caído o timeout | Backend 502; flash “Servicio externo no disponible”. |
| Película duplicada por `origen_api` + `id_api` | Backend 400 con id existente. Si está inactiva, el mensaje sugiere reactivarla. La UI marca “Ya cargada”. |
| Película con funciones programadas | La baja lógica la oculta de la cartelera, pero las funciones siguen existiendo. La UI advierte que primero deben cancelarse las funciones (Tarea 2). |
| Sesión expirada entre el decorador y la llamada | Se limpia la sesión y se redirige a login con flash. |
| Backend caído | `consultar_backend` devuelve 502; la página muestra flash y no rompe. |
| Formulario con duración/año no numéricos | Se detecta en la ruta antes de llamar al backend; flash y no se envía. |
| Sin géneros seleccionados | Backend 400; flash “Seleccioná al menos un género”. |
| Película inactiva | Se muestra en la tabla con badge “Inactiva” y botón “Reactivar”. |
| Edición de película OMDB | No se vuelve a consultar OMDb; se editan los campos locales manualmente. |

---

## 10. Pruebas y QA

### 10.1 Verificación de sintaxis

```bash
python -m compileall backend/src frontend
```

### 10.2 Pruebas de backend con `curl`

1. Login admin y guardar token:
   ```bash
   TOKEN=$(curl -s -X POST http://127.0.0.1:5000/auth/login \
     -H 'Content-Type: application/json' \
     -d '{"email":"admin@cineparadiso.com","contrasena":"Admin1234!"}' \
     | python -c 'import sys,json; print(json.load(sys.stdin)["token"])')
   ```
2. Listado admin:
   ```bash
   curl -s http://127.0.0.1:5000/peliculas/admin \
     -H "Authorization: Bearer $TOKEN"
   ```
3. Búsqueda OMDb:
   ```bash
   curl -s "http://127.0.0.1:5000/peliculas/externas/buscar?query=Dune" \
     -H "Authorization: Bearer $TOKEN"
   ```
4. Detalle OMDb:
   ```bash
   curl -s "http://127.0.0.1:5000/peliculas/externas/tt15239678" \
     -H "Authorization: Bearer $TOKEN"
   ```
5. Alta:
   ```bash
   curl -s -X POST http://127.0.0.1:5000/peliculas \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"titulo":"Dune: Part Two","sinopsis":"...","poster_url":"...","duracion_min":166,"clasificacion":"PG-13","anio_estreno":2024,"origen_api":"OMDB","id_api":"tt15239678","generos_ids":[2,3]}'
   ```
6. Edición:
   ```bash
   curl -s -X PUT http://127.0.0.1:5000/peliculas/<id> \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"clasificacion":"+13","activa":true}'
   ```
7. Baja y reactivación:
   ```bash
   curl -s -X DELETE http://127.0.0.1:5000/peliculas/<id> \
     -H "Authorization: Bearer $TOKEN"
   curl -s -X PUT http://127.0.0.1:5000/peliculas/<id> \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"activa":true}'
   ```

### 10.3 Pruebas de permisos

- Sin token → `401`.
- Token de cliente (`cliente@cineparadiso.com`) → `403`.
- Token de admin → `200`/`201`.
- Acceso web `/admin/peliculas` sin sesión → redirect a login/home con flash.
- Acceso web con cliente → redirect con “Acceso denegado”.

### 10.4 Pruebas manuales de UI

- [ ] La vista carga sin errores con backend y MySQL activos.
- [ ] La tabla muestra activas e inactivas.
- [ ] Buscar “Dune” devuelve resultados.
- [ ] Seleccionar un resultado precarga título, año, póster, sinopsis, duración, clasificación y géneros.
- [ ] El póster se previsualiza al editar la URL.
- [ ] Alta exitosa: aparece en la tabla y en MySQL.
- [ ] Alta duplicada: muestra error claro.
- [ ] Edición exitosa: los cambios se reflejan en la tabla.
- [ ] Baja: el modal confirma, la película queda inactiva y desaparece de la cartelera pública.
- [ ] Reactivación: vuelve a estado activo.
- [ ] Si se borra `OMDB_API_KEY` o se usa una inválida, la UI muestra error y permite carga manual.
- [ ] La vista es usable en 360px, 768px y escritorio.
- [ ] No hay `fetch`, `axios`, `XMLHttpRequest` ni WebSockets en `admin_peliculas.js`.
- [ ] La vista `client/checkout.html` sigue renderizando sus 4 campos igual que antes de extender `campo_formulario.html`.
- [ ] Búsqueda de duplicación: `grep` sobre los archivos nuevos para detectar bloques repetidos antes de commitear.

### 10.5 Verificación en MySQL

```sql
SELECT id_pelicula, titulo, origen_api, id_api, activa
FROM peliculas
ORDER BY id_pelicula DESC;

SELECT pg.id_pelicula, g.nombre
FROM pelicula_generos pg
JOIN generos g ON g.id_genero = pg.id_genero
WHERE pg.id_pelicula = <id>;
```

---

## 11. Criterios de aceptación

- [ ] Existe la vista `/admin/peliculas` y solo es accesible para `ADMINISTRADOR`.
- [ ] El listado incluye películas activas e inactivas, con géneros y estado.
- [ ] El buscador OMDb funciona y muestra resultados.
- [ ] Al seleccionar un resultado se precargan título, póster, sinopsis, duración y clasificación.
- [ ] El formulario de alta guarda en MySQL y refresca el listado.
- [ ] Se puede editar una película existente.
- [ ] Se puede dar de baja lógica y reactivar una película.
- [ ] Los errores de OMDb y del backend se muestran con `flash()`.
- [ ] No se usan `fetch`, `axios`, AJAX, WebSockets ni ORMs.
- [ ] No se agregaron dependencias.
- [ ] `docs/swagger.yaml` documenta los dos endpoints nuevos.
- [ ] La vista es responsive y respeta el design system.
- [ ] No hay código duplicado evitable (D10):
  - [ ] Las 6 rutas web delegan en `_leer_formulario()`, `_renderizar_pagina()` y `_redirigir_sesion_expirada()`; ninguna repite la carga de películas/géneros.
  - [ ] Un único `SQL_SELECCIONAR_PELICULAS_ADMIN`; el resto reutiliza las consultas existentes.
  - [ ] `listar_peliculas_admin()` reutiliza `_formatear_peliculas()`; el detalle externo reutiliza `_api_externa_no_disponible()`.
  - [ ] Un único componente de input (`campo_formulario.html` extendido) y un único componente de botón (`button.html`).
  - [ ] Un único modal de confirmación reutilizado por todas las bajas.
  - [ ] `admin_peliculas.css` no contiene colores hardcodeados: solo `var(--token)`.
  - [ ] `admin_peliculas.js` tiene una sola función `abrirModal()`/`cerrarModal()` y un solo listener de preview de póster.
- [ ] Extender `campo_formulario.html` no rompió `client/checkout.html` (se renderiza igual que antes).

---

## 12. Riesgos y mitigaciones

| Riesgo | Probabilidad | Mitigación |
| :--- | :--- | :--- |
| `OMDB_API_KEY` vacía o inválida | Alta | Documentar prerrequisito; error claro; permitir alta manual. |
| Límite de requests de OMDb | Media | Buscar solo al enviar el formulario; consultar detalle solo al seleccionar; no hacer N+1. |
| OMDb devuelve campos `"N/A"` | Alta | Normalizar a `null` y dejar que el admin complete. |
| Géneros OMDb no coinciden con los locales | Alta | Mapeo parcial + selección manual + aviso de no mapeados. |
| Duplicados al importar | Media | Backend bloquea; UI marca “Ya cargada” y ofrece editar/reactivar. |
| Baja de película con funciones activas | Media | Advertir en el modal; la baja es lógica; Tarea 2 gestiona funciones. |
| Conflictos de merge en `frontend/app.py`, `style.css` o navbar | Media | Cambios mínimos y localizados; no tocar navbar (Tarea 11). |
| `frontend/.env` sin `SECRET_KEY` | Alta en local | Prerrequisito de entorno documentado; no commitear secretos. |
| El backend cambia el contrato durante la implementación | Baja | Actualizar `docs/swagger.yaml` en el mismo commit que el código. |

---

## 13. Orden de commits sugerido

1. `[Peliculas][Backend] Agregar listado admin y detalle OMDb`
   - `constants.py`, `peliculas_repository.py`, `peliculas_validators.py`, `peliculas_services.py`, `peliculas_routes.py`, `docs/swagger.yaml`.
2. `[Peliculas][Frontend] Agregar servicios y utilidades de ABM`
   - `frontend/services/admin_peliculas_service.py`, `frontend/services/peliculas_service.py`, `frontend/utils/peliculas.py`.
3. `[Peliculas][Frontend] Agregar rutas web del backoffice`
   - `frontend/routes/admin_peliculas_routes.py`, `frontend/app.py`.
4. `[Peliculas][Frontend] Agregar vista, componentes y estilos`
   - `frontend/templates/backoffice/peliculas.html`, componentes, `admin_peliculas.css`, `modal.css`, `style.css`, `admin_peliculas.js`, enlace en dashboard.
5. `[Peliculas][Docs] Actualizar contrato y documentación de la tarea`
   - `docs/swagger.yaml` (si no se incluyó antes), notas en `docs/hito-3-tareas.md` si corresponde.

---

## 14. Resumen de archivos

### Nuevos

```text
docs/tasks/01_plan_ABM+OMDb.md
frontend/services/admin_peliculas_service.py
frontend/routes/admin_peliculas_routes.py
frontend/templates/backoffice/peliculas.html
frontend/templates/components/formulario_pelicula.html
frontend/templates/components/pelicula_externa_resultado.html
frontend/templates/components/modal_confirmacion.html
frontend/static/css/pages/admin_peliculas.css
frontend/static/css/components/modal.css
frontend/static/js/admin_peliculas.js
```

### Modificados

```text
backend/src/constants.py
backend/src/repositories/peliculas_repository.py
backend/src/validators/peliculas_validators.py
backend/src/services/peliculas_services.py
backend/src/routes/peliculas_routes.py
docs/swagger.yaml
frontend/services/peliculas_service.py
frontend/utils/peliculas.py
frontend/app.py
frontend/templates/backoffice/dashboard.html
frontend/templates/components/campo_formulario.html
frontend/static/css/style.css
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

Estas decisiones fueron consultadas y **aprobadas por el equipo**. No quedan preguntas abiertas: el plan se puede implementar tal como está.

1. **Edición completa: SÍ.**
   Se implementa el ABM completo (alta, baja, modificación y reactivación) sobre `PUT /peliculas/<id>`. No se entrega un MVP recortado.

2. **Endpoints nuevos de backend: AUTORIZADOS.**
   Se agregan `GET /peliculas/admin` (listado completo para el backoffice) y `GET /peliculas/externas/<id_api>` (detalle OMDb con sinopsis, duración y clasificación). Ambos quedan documentados en `docs/swagger.yaml` y protegidos con `validar_admin()`.

3. **Clasificación de OMDb: se muestra tal cual y la ajusta el admin.**
   OMDb puede devolver `PG-13`, `R`, `PG`, etc. Ese valor se precarga en el campo y el administrador lo cambia a `ATP`, `+13`, `+16` o `+18` según corresponda. No se hace un mapeo automático a la clasificación argentina.

4. **Navbar: NO se modifica en esta tarea.**
   El acceso a la vista se agrega únicamente desde el header de `frontend/templates/backoffice/dashboard.html`. El navbar queda intacto para la Tarea 11 y así se evitan conflictos de merge.

5. **Alcance: flujo completo integrado con frontend.**
   La entrega incluye backend + rutas web + servicios HTTP + templates + componentes + CSS + JS. No se considera terminada una acción que solo funcione por `curl`: tiene que ser operable desde el navegador por un administrador.

---

## 16. Próximo paso

1. Implementar la Fase 1 (backend) con la skill `02-desarrollar-backend`.
2. Implementar las fases 2 a 5 (frontend) con la skill `03-desarrollar-frontend`.
3. Ejecutar el QA de la sección 10 (end-to-end desde el navegador, no solo `curl`).
4. Auditar y commitear con la skill `04-revisar-y-commitear`, respetando el orden de commits de la sección 13.

**No se escribió código de la feature todavía. Solo se creó este documento de planificación.**
