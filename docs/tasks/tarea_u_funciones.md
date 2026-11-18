# Plan de implementación — ABM de Funciones (Backoffice Admin)

- **Tarea:** Programación y ABM de Funciones en Salas (Hito 3 — Tarea 2).
- **Rama sugerida:** `feature/admin-funciones` (creada desde `develop`).
- **Módulo:** Backoffice de Administración.
- **Estado:** Implementado y verificado en local. Pendiente de commit en una rama de trabajo y Pull Request hacia `develop`.
- **Documentos base:** `AGENTS.md`, `docs/hito-3-tareas.md`, `docs/swagger.yaml`, `docs/tasks/01_plan_ABM+OMDb.md`, `docs/tasks/02_plan_ABM+servicios.md`.
- **Implementación de referencia:** ABM de Películas y ABM de Servicios (mismos patrones de rutas, servicios HTTP, componentes y estilos).

---

## 1. Objetivo

Permitir que un usuario con rol `ADMINISTRADOR` administre la programación de funciones desde el backoffice:

1. Listar **todas** las funciones, incluyendo programadas, en curso, canceladas y finalizadas.
2. Dar de alta una función eligiendo película, complejo, sala, fecha, hora, formato, idioma, subtítulos y precio.
3. Editar una función existente (película, sala, horario, formato, idioma, subtítulos, precio y estado).
4. Dar de baja una función mediante cancelación lógica, sin borrar el registro histórico.
5. Respetar las reglas de negocio ya existentes: duración calculada, sala sin solapamientos y protección de entradas vendidas.
6. Todo mediante **SSR con Flask + Jinja2**, sin `fetch()`, `axios`, AJAX ni WebSockets.

### Fuera de alcance

- Reactivación de funciones canceladas: `CANCELADA` y `FINALIZADA` son estados terminales (`ESTADOS_FUNCION_TERMINALES`). El ABM no reabre funciones; la baja es definitiva a nivel operativo.
- Mapa de butacas y flujo de compra del cliente (Tareas 7 y 9).
- ABM de películas, servicios o validador QR.
- Cambios de esquema en MySQL, nuevas dependencias o cambios en `requirements.txt`.
- Rediseño global del navbar (Tarea 11). Solo se agrega el acceso desde el dashboard.

---

## 2. Requisitos y trazabilidad

| Requisito | Fuente | Cómo se cumple |
| :--- | :--- | :--- |
| Vista solo para administradores en `/admin/funciones` | Hito 3 — Tarea 2 | Blueprint protegido con `@admin_required` en todas las rutas web. |
| Listado de funciones vigentes con opción de cancelar | Hito 3 — Tarea 2 | `GET /funciones/admin` + tabla con acciones de edición y baja. |
| Selectores de Película, Complejo y Sala | Hito 3 — Tarea 2 | Formulario con selects SSR; salas agrupadas por complejo y filtrado visual por JS de DOM. |
| Inputs de fecha, hora, formato y precio | Hito 3 — Tarea 2 | Formulario `formulario_funcion.html`; el servidor arma el `DATETIME` de inicio. |
| ABM completo (alta, baja y modificación) | Título “ABM” + enunciado | `POST`, `PUT` y `DELETE` del backend, con rutas web `POST` y `POST/Redirect/GET`. |
| Prohibido `fetch`/AJAX | `AGENTS.md` | Toda comunicación pasa por `frontend/services/` con `requests`. |
| Prohibido ORM y clases | `AGENTS.md` | Funciones procedurales y SQL parametrizado en repositorios. |
| No agregar dependencias | `AGENTS.md` | Flask, `requests`, PyMySQL y Jinja2 ya están instalados. |
| Fechas en un único campo `DATETIME` | `AGENTS.md` | El formulario separa fecha/hora solo en la UI; el backend recibe y persiste un único `inicio` y calcula `fin`. |
| Reutilización de componentes UI | `AGENTS.md` / skill 03 | Se reutilizan `button.html`, `campo_formulario.html`, `modal_confirmacion.html` y `modal.css`. |

---

## 3. Auditoría del estado actual

> Esta sección conserva el diagnóstico **previo** a la implementación. Las brechas marcadas abajo ya fueron resueltas; se mantiene como registro de por qué se tomaron las decisiones.

### 3.1 Backend disponible

| Endpoint | Auth real | Comportamiento actual | Diagnóstico |
| :--- | :--- | :--- | :--- |
| `GET /funciones` | Pública | Lista solo funciones vigentes (`PROGRAMADA`/`EN_CURSO` y `fin > ahora`). | Sirve para el cliente, **no** para el ABM: no muestra canceladas ni finalizadas. |
| `POST /funciones` | **Sin validación de admin** | Crea una función, calcula `fin` con la duración de la película y controla solapamiento. | La docstring dice “Solo Admin”, pero la ruta no llama a `validar_admin()`. Es una brecha de seguridad. |
| `PUT /funciones/<id>` | **Sin validación de admin** | Solo permite `inicio`, `precio_entrada` y `estado`. | No permite editar película, sala, formato, idioma ni subtítulos. Insuficiente para un ABM alineado. |
| `DELETE /funciones/<id>` | **Sin validación de admin** | Cancela si no hay entradas activas; repetir la baja no falla. | Correcto en regla de negocio, pero sin autorización. |
| `GET /funciones/<id>/butacas` | Pública | Devuelve el mapa de butacas de la función. | Fuera del alcance del ABM. |
| `GET /funciones/<id>` | No existe | — | No se creará: la edición se resuelve desde el listado admin, igual que el ABM de Servicios. |
| `GET /funciones/admin` | No existe | — | **Brecha principal:** sin este endpoint el backoffice no puede listar todos los estados. |

### 3.2 Frontend actual (implementación parcial)

Existe una implementación incompleta que **no debe conservarse**:

| Archivo actual | Problema |
| :--- | :--- |
| `frontend/routes/admin_funciones_routes.py` | Usa `requests` directo y hardcodea `http://127.0.0.1:5000`. Duplica la llamada a `/funciones`. No usa `@admin_required`. No usa `api_client`. El “editar” hace `DELETE` + `POST`, lo que pierde el `id_funcion`, puede fallar por solapamiento y rompe la trazabilidad. |
| `frontend/services/funciones_service.py` | Solo cubre lectura pública y butacas; no tiene operaciones de ABM. |
| `frontend/templates/backoffice/funciones_lista.html` | HTML con estilos inline, sin componentes, sin estados, sin formulario integrado y sin datos de película/local. |
| `frontend/templates/backoffice/funciones_form.html` | Pide IDs numéricos a mano en lugar de selects. Envía `idioma` en el campo `formato` y fuerza `precio_entrada = 6500`. No edita `id_pelicula`/`id_sala` correctamente. |
| `backend/funciones_lista.html` | Archivo huérfano fuera de la carpeta de templates. No se usa. |
| `frontend/app.py` | El blueprint `admin_funciones_bp` ya está registrado. No requiere cambios, solo verificación. |

### 3.3 Activos reutilizables del proyecto

| Activo | Uso en esta tarea |
| :--- | :--- |
| `frontend/services/api_client.py` → `consultar_backend()` | Único cliente HTTP; GET/POST/PUT/DELETE con Bearer y errores 502. |
| `frontend/utils/auth.py` → `@admin_required` | Protección de todas las rutas web del backoffice. |
| `frontend/utils/errores.py` → `extraer_mensaje_error()` | Mensajes legibles para `flash()`. |
| `frontend/utils/formatos.py` | `formatear_fecha_corta`, `formatear_hora`, `formatear_precio`. |
| `frontend/templates/layout.html` | Estructura base, navbar y mensajes flash globales. |
| `frontend/templates/components/button.html` | Botones y enlaces con variantes `primary`/`secondary`/`danger`. |
| `frontend/templates/components/campo_formulario.html` | Inputs con `valor`, `tipo`, `minimo`, `maximo`, `obligatorio`, `maxlength`. |
| `frontend/templates/components/modal_confirmacion.html` | Modal de confirmación de baja. |
| `frontend/static/css/components/modal.css` | Comportamiento visual del modal. |
| `frontend/static/css/pages/admin_servicios.css` | Patrón de cabecera, formulario desplegable, tabla y badges. |
| `frontend/static/css/pages/admin_peliculas.css` | Patrón de tabla, badges de estado y acciones. |
| `frontend/static/js/admin_peliculas.js` | Lógica de modales y apertura del formulario que se extraerá a un módulo compartido. |
| `backend/src/utils.py` | `validar_admin`, `formatear_funcion`, `error_validacion`, `error_conflicto`, `error_no_encontrado`, `parsear_datetime`, `validar_*`. |
| `backend/src/constants.py` | `ESTADOS_FUNCION`, `ESTADOS_FUNCION_TERMINALES`, `FORMATOS_SALA`, `DURACION_FUNCION_POR_DEFECTO_MIN`. |
| `backend/src/repositories/salas_repository.py` | `obtener_locales_db`, `obtener_salas_por_local_db`. |
| Endpoints `GET /locales` y `GET /locales/<id>/salas` | Alimentan los selects de complejo y sala. |
| Endpoint `GET /peliculas/admin` | Alimenta el select de películas (se filtran las activas). |

---

## 4. Decisiones de diseño

### D1 — SSR puro, sin llamadas desde el navegador

El navegador solo envía formularios `GET`/`POST` al frontend Flask. El frontend llama al backend con `requests` a través de `consultar_backend()`. El JavaScript solo manipula el DOM: abre/cierra modales, alterna el formulario y filtra opciones de sala ya renderizadas.

### D2 — Endpoint admin separado para el listado completo

`GET /funciones` es un contrato público del cliente (solo funciones vigentes). Cambiar su comportamiento según el token rompería la cartelera. Se agrega `GET /funciones/admin`, protegido con `validar_admin()`, que devuelve todos los estados ordenados por inicio descendente.

### D3 — No se crea endpoint de detalle individual

Para editar, el frontend consume `GET /funciones/admin` y busca la función por `id_funcion` en memoria. Es el mismo patrón ya aprobado en el ABM de Servicios y evita duplicar una ruta que solo filtra una fila.

### D4 — `PUT /funciones/<id>` se extiende para el ABM completo

El endpoint actual solo acepta `inicio`, `precio_entrada` y `estado`. Se amplía para aceptar también `id_pelicula`, `id_sala`, `formato`, `idioma` y `subtitulada`, manteniendo todos los campos como opcionales y exigiendo al menos uno.

Reglas:
- Si cambia la película, se recalcula `fin = inicio + duración de la nueva película`. Si solo cambia el inicio, se conserva la duración original.
- Si cambia la sala, el inicio o la película, se valida solapamiento en la sala destino.
- Si la función tiene entradas `OCUPADA` o `RESERVADA`, se bloquean los cambios de programación (película, sala, inicio, formato, idioma, subtítulos) y la cancelación. Solo se permite cambiar el precio.
- No se permite modificar una función `CANCELADA` o `FINALIZADA`.
- La validación de película/sala activa se aplica solo cuando se cambia ese campo, para no bloquear una edición de precio si la sala fue deshabilitada después.

### D5 — Autorización explícita en todas las mutaciones

`POST`, `PUT` y `DELETE` de funciones pasan a llamar a `validar_admin(request.headers.get("Authorization"))`, igual que Películas y Servicios. `GET /funciones` y `GET /funciones/<id>/butacas` siguen siendo públicos.

### D6 — ABM de una sola página con formulario desplegable

Se sigue el patrón de `admin_servicios` y `admin_peliculas`: una única vista `backoffice/funciones.html` con listado y formulario integrado. `?nuevo=1` abre el formulario de alta; la edición abre el formulario precargado. Se evita navegar a una página separada.

### D7 — Selects SSR y filtrado visual por complejo

- Película: select con películas activas (`GET /peliculas/admin`, filtrando `activa`).
- Complejo: select con locales activos (`GET /locales`).
- Sala: select con todas las salas activas, agrupadas por complejo con `<optgroup>` y atributo `data-local`.
- El JS filtra las opciones de sala según el complejo elegido. Si JavaScript no está disponible, el select sigue mostrando todas las salas y el formulario funciona igual.
- En edición, si la sala actual está inactiva, se incluye como opción marcada para no perder el dato.

### D8 — Extracción de la lógica de modales a un módulo compartido

`admin_peliculas.js` contiene la lógica genérica de abrir/cerrar modales y confirmar bajas. Para no duplicarla en funciones, se crea `frontend/static/js/modal.js` y se reutiliza en:
- `backoffice/funciones.html`
- `backoffice/peliculas.html`
- `backoffice/servicios.html`

Cada JS de página conserva solo su comportamiento específico (preview de póster, filtro local→sala, apertura del formulario). Los modales se renderizan **fuera de la tabla**: dentro de un `<tbody>` el parser HTML cierra el `<form>` y los botones quedan fuera, por lo que la confirmación no funciona.

### D9 — Sin cambios de esquema ni dependencias

La tabla `funciones` ya tiene todos los campos necesarios. No se agregan columnas, tablas ni paquetes.

### D10 — Regla anti-duplicación y modularidad

| Responsabilidad | Único lugar autorizado | Prohibido |
| :--- | :--- | :--- |
| Llamadas HTTP al backend | `frontend/services/*.py` vía `consultar_backend()` | `requests` directo en rutas o templates |
| Autorización de vistas | `@admin_required` | Chequeos manuales de rol |
| Mensajes de error | `extraer_mensaje_error()` | `respuesta["errors"][0]` repetido |
| SQL | `backend/src/repositories/*.py` con `%s` | SQL en services/routes |
| Reglas de función | `backend/src/services/funciones_services.py` | duplicar reglas en rutas |
| Formato de respuesta | `backend/src/utils.py` → `formatear_funcion()` | `_formatear_funcion()` local duplicado |
| Inputs de formulario | `components/campo_formulario.html` y selects del formulario específico | HTML de input repetido por página |
| Botones | `components/button.html` | HTML de botón suelto |
| Modal | `components/modal_confirmacion.html` + `static/js/modal.js` | lógica de modal duplicada por página |
| Tokens de diseño | `static/css/tokens.css` | hex hardcodeados en CSS de página |

### D11 — La edición envía solo los campos modificados

El backend valida `inicio` como fecha futura cada vez que se envía. Si el formulario reenviara todos los campos, editar una función `EN_CURSO` (o cualquier función con inicio pasado) fallaría aunque el usuario solo cambie el precio. Por eso `_payload_actualizacion()` compara el formulario con la función actual y envía únicamente los campos que cambiaron:

- Si no hay cambios, muestra “No se detectaron cambios en la función” y no llama al `PUT`.
- `inicio` se compara con precisión de **minutos**, porque el formulario no maneja segundos. Así una función `EN_CURSO` con `inicio = 01:13:42` no se considera modificada al reenviar `01:13`.
- Los campos de programación no enviados no se revalidan ni se chequean contra solapamientos.

### D12 — Fecha mínima del formulario en edición

El input `fecha` usa `min = hoy` para altas. En edición, si la función empezó antes de medianoche y sigue `EN_CURSO`, el mínimo se ajusta a la fecha de inicio de esa función para que el navegador no bloquee un cambio de precio. El backend sigue rechazando cualquier `inicio` pasado que se envíe explícitamente.

---

## 5. Contrato de datos

### 5.1 Función (respuesta del backend)

```json
{
  "id_funcion": 1,
  "id_pelicula": 1,
  "titulo_pelicula": "Dune: Parte Dos",
  "id_sala": 1,
  "numero_sala": 1,
  "nombre_local": "Cine Paradiso Centro",
  "inicio": "2026-11-24T20:00:00",
  "fin": "2026-11-24T22:46:00",
  "formato": "4D",
  "idioma": "Inglés",
  "subtitulada": true,
  "precio_entrada": 6500.0,
  "estado": "PROGRAMADA"
}
```

### 5.2 Listado admin (`GET /funciones/admin`)

- **Auth:** Bearer token de `ADMINISTRADOR`.
- **Respuesta 200:** array de `FuncionItem`, incluyendo todos los estados.
- **Orden:** `inicio DESC` (las más recientes primero).
- **Errores:** `401` token ausente/inválido, `403` usuario sin rol admin.

### 5.3 Alta (`POST /funciones`)

```json
{
  "id_pelicula": 1,
  "id_sala": 1,
  "inicio": "2026-11-24T20:00:00",
  "formato": "4D",
  "idioma": "Inglés",
  "subtitulada": true,
  "precio_entrada": 6500.00
}
```

- `estado` siempre se persiste como `PROGRAMADA`.
- `fin` se calcula con `duracion_min` de la película o `DURACION_FUNCION_POR_DEFECTO_MIN`.

### 5.4 Edición (`PUT /funciones/<id>`)

Todos los campos son opcionales, pero debe enviarse al menos uno:

```json
{
  "id_pelicula": 1,
  "id_sala": 2,
  "inicio": "2026-11-25T21:00:00",
  "formato": "3D",
  "idioma": "Español",
  "subtitulada": false,
  "precio_entrada": 7000.00,
  "estado": "PROGRAMADA"
}
```

### 5.5 Baja (`DELETE /funciones/<id>`)

- Cancela lógicamente: `estado = 'CANCELADA'`.
- No borra la fila.
- Si ya estaba cancelada, responde 200 con el mismo mensaje (idempotente).
- Si está `FINALIZADA` o tiene entradas activas, responde 400/409 según la regla existente.

### 5.6 Reglas de validación

| Campo | Regla |
| :--- | :--- |
| `id_pelicula` | Entero positivo; la película debe existir y estar activa al crear o al cambiar. |
| `id_sala` | Entero positivo; la sala debe existir y estar activa al crear o al cambiar. |
| `inicio` | ISO 8601, fecha futura; se parsea con `parsear_datetime()`. |
| `formato` | `2D`, `3D` o `4D` (`FORMATOS_SALA`). |
| `idioma` | Texto opcional de hasta 50 caracteres; vacío se normaliza a `null`. |
| `subtitulada` | Booleano. |
| `precio_entrada` | Decimal positivo. |
| `estado` | `PROGRAMADA`, `EN_CURSO`, `CANCELADA` o `FINALIZADA` (`ESTADOS_FUNCION`). |
| Solapamiento | La sala no puede tener otra función no cancelada ni finalizada en `[inicio, fin)`. |
| Entradas activas | `OCUPADA` o `RESERVADA` bloquean reprogramación y cancelación. |

---

## 6. Plan paso a paso por archivo

### Fase 0 — Prerrequisitos de entorno

1. Confirmar rama:
   ```bash
   git branch --show-current
   # Debe ser feature/admin-funciones (o crearla desde develop)
   ```
2. Confirmar MySQL levantado en `backend/.env` (`DB_PORT=3306`).
3. Confirmar credenciales del seed:
   - Admin: `admin@cineparadiso.com` / `Admin1234!`
   - Cliente: `cliente@cineparadiso.com` / `Cliente1234!`
4. Confirmar que `backend/.venv` y `frontend/.venv` tienen las dependencias instaladas.
5. Confirmar que `frontend/.env` tiene `SECRET_KEY` de al menos 32 caracteres.

> Estado actual verificado: MySQL responde, los `.env` existen y los entornos virtuales están creados. La tabla `funciones` está vacía en la base local; las pruebas de alta deben crear datos con fechas futuras.

---

### Fase 1 — Backend

#### 1.1 `backend/src/repositories/funciones_repository.py`

**Agregar** una consulta admin reutilizando la constante `SELECT_FUNCION_DETALLE`:

```python
def obtener_funciones_admin_db() -> list[dict]:
    """Lista todas las funciones, incluyendo canceladas y finalizadas, para el ABM."""
    query = SELECT_FUNCION_DETALLE + " ORDER BY f.inicio DESC;"
    return ejecutar_consulta(query)
```

**Modificar** `actualizar_funcion_db()` para actualizar todos los campos editables:

```python
def actualizar_funcion_db(id_funcion: int, datos: dict) -> int:
    """Actualiza película, sala, horario, formato, idioma, subtítulos, precio y estado."""
    query = """
        UPDATE funciones
        SET id_pelicula = %s, id_sala = %s, inicio = %s, fin = %s,
            formato = %s, idioma = %s, subtitulada = %s,
            precio_entrada = %s, estado = %s
        WHERE id_funcion = %s;
    """
    valores = (
        datos["id_pelicula"],
        datos["id_sala"],
        datos["inicio"],
        datos["fin"],
        datos["formato"],
        datos["idioma"],
        datos["subtitulada"],
        datos["precio_entrada"],
        datos["estado"],
        id_funcion,
    )
    return ejecutar_mutacion(query, valores)
```

No modificar `obtener_funciones_db`, `insertar_funcion_db`, `cancelar_funcion_db` ni `obtener_estado_butacas_funcion_db`.

#### 1.2 `backend/src/services/funciones_services.py`

**Eliminar** `_formatear_funcion()` local y **reutilizar** `formatear_funcion` de `src.utils` (ya lo usa el módulo de películas). Esto elimina duplicación de formato.

**Agregar helpers privados** para no repetir reglas:

```python
def _obtener_pelicula_activa(id_pelicula: int) -> dict:
    pelicula = buscar_pelicula_para_funcion_db(id_pelicula)
    if pelicula is None or not pelicula["activa"]:
        raise error_validacion("La película indicada no existe o está dada de baja.")
    return pelicula


def _obtener_sala_activa(id_sala: int) -> dict:
    sala = buscar_sala_para_funcion_db(id_sala)
    if sala is None or not sala["activa"]:
        raise error_validacion("La sala indicada no existe o está deshabilitada.")
    return sala


def _calcular_fin(inicio, duracion_min: int | None):
    duracion = duracion_min or DURACION_FUNCION_POR_DEFECTO_MIN
    return inicio + timedelta(minutes=duracion)
```

**Agregar** `listar_funciones_admin()`:

```python
def listar_funciones_admin() -> list[dict]:
    """Lista todas las funciones para el ABM, sin filtrar por estado ni vigencia."""
    return [formatear_funcion(f) for f in obtener_funciones_admin_db()]
```

**Refactorizar** `crear_funcion()` para usar los helpers:

```python
def crear_funcion(datos: dict) -> dict:
    pelicula = _obtener_pelicula_activa(datos["id_pelicula"])
    _obtener_sala_activa(datos["id_sala"])
    fin = _calcular_fin(datos["inicio"], pelicula["duracion_min"])
    _verificar_sala_libre(datos["id_sala"], datos["inicio"], fin)
    id_funcion = insertar_funcion_db({**datos, "fin": fin})
    return formatear_funcion(buscar_funcion_por_id_db(id_funcion))
```

**Reescribir** `actualizar_funcion()` con esta secuencia:

1. Obtener la función actual o lanzar 404.
2. Rechazar si el estado actual es terminal.
3. Calcular valores destino:
   - `id_pelicula`, `id_sala`, `inicio`, `formato`, `idioma`, `subtitulada`, `precio_entrada`, `estado`.
4. Detectar si cambia la programación:
   - `id_pelicula`, `id_sala`, `inicio`, `formato`, `idioma` o `subtitulada`.
5. Detectar si se cancela (`estado == "CANCELADA"`).
6. Consultar una sola vez `tiene_entradas_activas_db()`.
7. Si hay entradas activas y cambia la programación o se cancela → `error_conflicto(...)`.
8. Si cambia película o inicio → validar película activa y recalcular `fin`.
9. Si cambia sala o inicio o película → `_verificar_sala_libre(..., id_excluir=id_funcion)`.
10. Si cambia sala → validar sala activa.
11. Persistir con `actualizar_funcion_db()` y devolver la función actualizada.

**No modificar** `eliminar_funcion()` ni `obtener_mapa_butacas_funcion()` salvo el reemplazo de `_formatear_funcion` por `formatear_funcion` si corresponde.

#### 1.3 `backend/src/validators/funciones_validators.py`

**Ampliar** `validar_actualizar_funcion()`:

```python
def validar_actualizar_funcion(datos) -> dict:
    datos = validar_objeto_json(datos)
    cambios = {}
    if "id_pelicula" in datos:
        cambios["id_pelicula"] = validar_entero_positivo(datos["id_pelicula"], "id_pelicula")
    if "id_sala" in datos:
        cambios["id_sala"] = validar_entero_positivo(datos["id_sala"], "id_sala")
    if "inicio" in datos:
        cambios["inicio"] = _validar_inicio_futuro(datos["inicio"])
    if "formato" in datos:
        cambios["formato"] = validar_opcion(datos["formato"], FORMATOS_SALA, "formato")
    if "idioma" in datos:
        cambios["idioma"] = validar_texto_opcional(datos["idioma"], "idioma", 50)
    if "subtitulada" in datos:
        cambios["subtitulada"] = validar_booleano(datos["subtitulada"], "subtitulada")
    if "precio_entrada" in datos:
        cambios["precio_entrada"] = validar_decimal_positivo(
            datos["precio_entrada"], "precio_entrada"
        )
    if "estado" in datos:
        cambios["estado"] = validar_opcion(datos["estado"], ESTADOS_FUNCION, "estado")
    if not cambios:
        raise error_validacion(
            "Debe enviar al menos uno de: id_pelicula, id_sala, inicio, formato, "
            "idioma, subtitulada, precio_entrada o estado."
        )
    return cambios
```

Agregar `validar_texto_opcional` al import de `src.utils`.

#### 1.4 `backend/src/routes/funciones_routes.py`

- Importar `validar_admin` desde `src.utils`.
- Importar `listar_funciones_admin` desde el servicio.
- Agregar `GET /funciones/admin` **antes** de la ruta de butacas (por claridad, no por conflicto real):

```python
@app.route("/funciones/admin", methods=["GET"])
def get_funciones_admin():
    """GET /funciones/admin: Lista todas las funciones para el ABM (Solo Admin)."""
    validar_admin(request.headers.get("Authorization"))
    return jsonify(listar_funciones_admin()), 200
```

- En `post_funcion`, `put_funcion` y `delete_funcion`, agregar como primera línea:
  ```python
  validar_admin(request.headers.get("Authorization"))
  ```

#### 1.5 `docs/swagger.yaml`

- Documentar `GET /funciones/admin`:
  - tag `Funciones`
  - `security: BearerAuth`
  - respuesta `200` con array de `FuncionItem`
  - respuestas `401` y `403`
- Ampliar `FuncionActualizarRequest` con:
  - `id_pelicula`
  - `id_sala`
  - `formato`
  - `idioma`
  - `subtitulada`
- Actualizar la descripción del `PUT /funciones/{id}`: “Modifica la programación, el precio o el estado de una función”.
- Confirmar que `POST`, `PUT` y `DELETE` ya declaren `BearerAuth`; el código ahora lo exige de verdad.

---

### Fase 2 — Frontend: servicios y utilidades

#### 2.1 `frontend/services/admin_funciones_service.py` (nuevo)

Único punto de contacto con la API para el ABM:

```python
from services.api_client import consultar_backend


def listar_funciones_admin(token: str):
    """Obtiene todas las funciones, incluyendo canceladas y finalizadas, para el ABM."""
    return consultar_backend("/funciones/admin", token, metodo="GET")


def listar_peliculas_admin(token: str):
    """Obtiene las películas para el select; la ruta filtra las activas."""
    return consultar_backend("/peliculas/admin", token, metodo="GET")


def listar_locales(token: str):
    """Obtiene los complejos activos para el select."""
    return consultar_backend("/locales", token, metodo="GET")


def listar_salas_por_local(token: str, id_local: int):
    """Obtiene las salas de un complejo para el select."""
    return consultar_backend(f"/locales/{id_local}/salas", token, metodo="GET")


def crear_funcion(token: str, datos: dict):
    """Programa una función nueva."""
    return consultar_backend("/funciones", token, metodo="POST", datos=datos)


def actualizar_funcion(token: str, id_funcion: int, datos: dict):
    """Modifica una función existente."""
    return consultar_backend(
        f"/funciones/{id_funcion}", token, metodo="PUT", datos=datos
    )


def dar_de_baja_funcion(token: str, id_funcion: int):
    """Cancela lógicamente una función."""
    return consultar_backend(f"/funciones/{id_funcion}", token, metodo="DELETE")
```

No usar `requests` directo. No hardcodear la URL del backend.

#### 2.2 `frontend/utils/funciones.py` (nuevo)

Utilidades de presentación y armado de formulario:

```python
from datetime import datetime

from utils.formatos import formatear_fecha_corta, formatear_hora, formatear_precio

ESTADOS_FUNCION_TERMINALES = {"CANCELADA", "FINALIZADA"}


def combinar_salas(locales: list[dict], salas_por_local: dict) -> list[dict]:
    """Aplana las salas y les agrega el nombre del complejo para el select."""
    ...


def preparar_funcion_para_tabla(funcion: dict) -> dict:
    """Agrega fecha/hora/precio legibles, clase de badge y permisos de acción."""
    ...


def preparar_funciones_para_tabla(funciones: list[dict]) -> list[dict]:
    ...


def borrador_desde_funcion(funcion: dict) -> dict:
    """Convierte una función del backend en valores crudos para el formulario."""
    ...


def armar_inicio_iso(fecha: str, hora: str) -> str:
    """Valida fecha/hora del formulario y devuelve 'YYYY-MM-DDTHH:MM:SS'."""
    ...
```

Reglas:
- `preparar_funcion_para_tabla` debe marcar `puede_editar` y `puede_baja` como `False` para estados terminales.
- `borrador_desde_funcion` debe separar `inicio` en `fecha` y `hora` y resolver `id_local` desde `nombre_local` (o desde el listado de salas).
- `armar_inicio_iso` debe lanzar `ValueError` con un mensaje en castellano si la fecha/hora no es válida.

#### 2.3 `frontend/services/funciones_service.py`

No modificar. Sigue siendo el cliente público para cartelera, butacas y compra. El ABM usa el servicio admin nuevo.

---

### Fase 3 — Frontend: rutas web

#### 3.1 `frontend/routes/admin_funciones_routes.py` (reescritura completa)

Estructura obligatoria:

```python
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.admin_funciones_service import (
    actualizar_funcion,
    crear_funcion,
    dar_de_baja_funcion,
    listar_funciones_admin,
    listar_locales,
    listar_peliculas_admin,
    listar_salas_por_local,
)
from utils.auth import admin_required
from utils.errores import extraer_mensaje_error
from utils.funciones import (
    armar_inicio_iso,
    borrador_desde_funcion,
    combinar_salas,
    preparar_funciones_para_tabla,
)

admin_funciones_bp = Blueprint("admin_funciones", __name__, url_prefix="/admin/funciones")
```

Funciones privadas:

- `_redirigir_sesion_expirada()`: limpia `access_token` y `usuario`, flash y redirige a `auth.login`.
- `_borrador_vacio()`: claves `id_pelicula`, `id_sala`, `id_local`, `fecha`, `hora`, `formato`, `idioma`, `subtitulada`, `precio_entrada`.
- `_leer_formulario(form)`: lee el formulario y devuelve un borrador con tipos corregidos; usa `armar_inicio_iso`.
- `_cargar_contexto(token)`: consulta funciones admin, películas admin, locales y salas por local; devuelve `(funciones, peliculas_activas, locales, salas, error_backend, redireccion)`.
- `_renderizar_pagina(...)`: centraliza el render de `backoffice/funciones.html`.

Rutas:

| Método | Ruta | Acción |
| :--- | :--- | :--- |
| `GET` | `/admin/funciones` | Lista todas las funciones. Si `?nuevo=1`, abre el formulario de alta. |
| `POST` | `/admin/funciones` | Crea una función y redirige al listado. |
| `GET` | `/admin/funciones/<int:id_funcion>/editar` | Busca la función en el listado admin y abre el formulario precargado. |
| `POST` | `/admin/funciones/<int:id_funcion>/editar` | Actualiza la función y redirige al listado. |
| `POST` | `/admin/funciones/<int:id_funcion>/eliminar` | Cancela la función y redirige al listado. |

Reglas de las rutas:
- Todas decoradas con `@admin_required`.
- `401/403` del backend → `_redirigir_sesion_expirada()`.
- Errores del backend → `flash(extraer_mensaje_error(...), "error")` y re-render con borrador.
- Altas y ediciones exitosas → `flash(..., "success")` + `redirect(url_for("admin_funciones.index"))` (POST/Redirect/GET).
- No usar `requests` directo.
- No repetir la lógica de carga en cada ruta: usar `_renderizar_pagina` y `_cargar_contexto`.

#### 3.2 `frontend/app.py`

Verificar que `admin_funciones_bp` siga registrado. No se requieren cambios funcionales. Si se toca el archivo, solo ordenar imports; evitar cambios innecesarios.

---

### Fase 4 — Frontend: plantillas y componentes

#### 4.1 `frontend/templates/backoffice/funciones.html` (nuevo)

Estructura:

1. `{% extends 'layout.html' %}`.
2. `extra_css` con `css/pages/admin_funciones.css`.
3. Cabecera de backoffice:
   - eyebrow “Backoffice”
   - título “Gestión de funciones”
   - subtítulo
   - links “Volver al dashboard” y “Volver a la cartelera”
   - botón “+ Nueva función” → `url_for('admin_funciones.index', nuevo=1)`
4. `error_backend` si existe.
5. Contenedor del formulario:
   - `id="contenedor-formulario"`
   - clase activa si `abrir_formulario`
   - incluye `components/formulario_funcion.html`
6. Tabla de funciones:
   - columnas: ID, Película, Complejo / Sala, Inicio, Fin, Formato, Idioma, Precio, Estado, Acciones.
   - badges de estado (`PROGRAMADA`, `EN_CURSO`, `CANCELADA`, `FINALIZADA`).
   - botón “Editar” solo si `funcion.puede_editar`.
   - botón “Dar de baja” solo si `funcion.puede_baja`.
   - formulario/modal de baja por fila con `components/modal_confirmacion.html`.
   - estado vacío con mensaje claro.
7. `extra_scripts`: `modal.js` y `admin_funciones.js`.

No incluir `components/mensajes.html`: `layout.html` ya renderiza los flashes globales. Evitar el doble mensaje que hoy ocurre en `servicios.html`.

#### 4.2 `frontend/templates/components/formulario_funcion.html` (nuevo)

Componente parametrizado. Variables recibidas:

| Variable | Uso |
| :--- | :--- |
| `borrador` | Valores actuales del formulario. |
| `peliculas` | Lista de películas activas. |
| `locales` | Lista de complejos. |
| `salas` | Lista aplanada de salas con `id_local`, `numero`, `nombre_local`, `activa`. |
| `modo_formulario` | `crear` o `editar`. |
| `accion_formulario` | URL de `POST` del frontend. |
| `id_funcion_editando` | ID para el título cuando se edita. |
| `formatos` | `("2D", "3D", "4D")`. |
| `fecha_minima` | `YYYY-MM-DD` para el atributo `min` del input date. |

Campos:

- **Película:** `<select name="id_pelicula" required>` con `titulo` y `duracion_min`.
- **Complejo:** `<select name="id_local" data-selector-local>` con `locales`.
- **Sala:** `<select name="id_sala" required>` con `<optgroup label="{{ local.nombre }}">` y `<option data-local="{{ sala.id_local }}">Sala {{ sala.numero }}</option>`.
- **Fecha:** `<input type="date" name="fecha" min="{{ fecha_minima }}" required>`.
- **Hora:** `<input type="time" name="hora" required>`.
- **Formato:** `<select name="formato" required>` con `2D`, `3D`, `4D`.
- **Idioma:** `<input type="text" name="idioma" maxlength="50">` opcional.
- **Subtitulada:** checkbox `name="subtitulada"`.
- **Precio:** `<input type="number" name="precio_entrada" min="0.01" step="0.01" max="99999999.99" required>`.
- Botones “Cancelar” y “Guardar cambios” / “Crear función” usando `components/button.html`.

El formulario **no** envía `id_local` al backend: es un campo auxiliar de UI. El backend recibe solo `id_sala`.

#### 4.3 `frontend/templates/components/modal_confirmacion.html`

Sin cambios funcionales. Se reutiliza tal cual. El modal de baja de funciones se renderiza por fila con:

```jinja
{% with id_modal='modal-baja-' ~ funcion.id_funcion,
        titulo='Confirmar baja de función',
        mensaje='¿Querés cancelar la función de "' ~ funcion.titulo_pelicula ~ '" del ' ~ funcion.fecha_legible ~ ' a las ' ~ funcion.hora_inicio ~ '? La función quedará cancelada y no se podrá reactivar.',
        accion=url_for('admin_funciones.eliminar', id_funcion=funcion.id_funcion),
        texto_confirmar='Sí, cancelar función',
        texto_cancelar='Volver' %}
  {% include 'components/modal_confirmacion.html' %}
{% endwith %}
```

#### 4.4 `frontend/templates/backoffice/dashboard.html`

Agregar un botón “Gestionar funciones” junto a “Gestionar películas” y “Gestionar servicios”:

```jinja
{% with texto='Gestionar funciones', url_destino=url_for('admin_funciones.index') %}
  {% include 'components/button.html' %}
{% endwith %}
```

No modificar el navbar (Tarea 11).

#### 4.5 Limpieza de plantillas legacy

Eliminar para evitar código muerto y duplicación:

- `frontend/templates/backoffice/funciones_lista.html`
- `frontend/templates/backoffice/funciones_form.html`
- `backend/funciones_lista.html` (archivo huérfano, no pertenece al backend)

La nueva vista `backoffice/funciones.html` y el componente `components/formulario_funcion.html` los reemplazan por completo.

---

### Fase 5 — Frontend: CSS y JavaScript

#### 5.1 `frontend/static/css/pages/admin_funciones.css` (nuevo)

Basado en `admin_servicios.css` y `admin_peliculas.css`, usando tokens de `tokens.css`.

Clases mínimas:

- `.admin-funciones`, `.admin-funciones__container`
- `.admin-funciones__header`, `__eyebrow`, `__title`, `__subtitle`, `__header-actions`, `__back`
- `.admin-funciones__form-container` y `--activo` (transición de max-height/opacity)
- `.formulario-funcion-card`, `__header`, `__cerrar`, `__grid`, `__campo`, `__campo--checkbox`, `__actions`
- `.admin-funciones__table-wrapper`, `__table`, `__actions-cell`, `__empty`
- `.badge-estado` y variantes `--programada`, `--en-curso`, `--cancelada`, `--finalizada`
- Ajustes responsive: tabla con scroll horizontal y grid de formulario a una columna en `< 768px`.

#### 5.2 `frontend/static/js/modal.js` (nuevo, compartido)

Extraer desde `admin_peliculas.js`:

- `abrirModal(modal)`
- `cerrarModal(modal)`
- listeners para `[data-modal-open]`, `[data-modal-close]`, tecla `Escape`.
- listener para `form[data-confirmar-baja]` que reescribe la acción del formulario del modal según `data-modal-destino`.

Incluir este script antes de los scripts de página en:

- `backoffice/peliculas.html`
- `backoffice/servicios.html`
- `backoffice/funciones.html`

Refactorizar `admin_peliculas.js` para eliminar la lógica duplicada de modales y conservar solo:
- preview del póster;
- scroll/foco del formulario cuando `data-abrir-formulario="true"`.

`admin_servicios.js` conserva solo el toggle `?nuevo=1` y foco.

#### 5.3 `frontend/static/js/admin_funciones.js` (nuevo)

Responsabilidades:

1. Si `?nuevo=1` o `data-abrir-formulario="true"`, mostrar el contenedor del formulario y enfocar el primer campo.
2. Filtrar las opciones de `id_sala` según el `id_local` elegido:
   - leer `data-local` de cada `<option>`;
   - ocultar/mostrar opciones;
   - si la sala seleccionada ya no pertenece al local, seleccionar la primera disponible.
3. Sin llamadas al backend, sin `fetch`, sin `axios`.

#### 5.4 `frontend/static/css/style.css`

No requiere cambios: las páginas admin cargan su CSS por `extra_css`. No agregar `admin_funciones.css` al manifest global para no cargarlo en todas las vistas.

---

### Fase 6 — Documentación y cierre

- Actualizar `docs/swagger.yaml` (Fase 1.5).
- Actualizar este plan solo si cambia una decisión durante la implementación.
- Verificar que no queden referencias a `funciones_lista.html` ni `funciones_form.html`.
- Verificar que `backend/funciones_lista.html` ya no exista.
- Actualizar `docs/tasks` con el registro de pruebas realizadas si el equipo lo considera necesario.

---

## 7. Flujos funcionales esperados

### 7.1 Listado

1. El admin entra a `/admin/funciones`.
2. `@admin_required` valida la sesión.
3. La ruta llama a `listar_funciones_admin(token)`.
4. El backend responde todas las funciones, incluyendo canceladas y finalizadas.
5. La ruta prepara fecha/hora/precio legibles y permisos de acción.
6. La vista muestra la tabla con badges de estado.
7. Si el backend falla, se muestra un flash y una tabla vacía sin romper la página.

### 7.2 Alta

1. El admin hace clic en “+ Nueva función”.
2. Se abre el formulario integrado (`?nuevo=1`).
3. Selecciona película, complejo, sala, fecha, hora, formato, idioma, subtítulos y precio.
4. El formulario envía `POST /admin/funciones` al frontend.
5. La ruta arma `inicio` como `YYYY-MM-DDTHH:MM:SS`, convierte tipos y llama a `crear_funcion(token, datos)`.
6. El backend valida, calcula `fin`, controla solapamiento y persiste `PROGRAMADA`.
7. El frontend muestra flash de éxito y redirige al listado.
8. Si hay error, se re-renderiza el formulario conservando los valores ingresados y el mensaje del backend.

### 7.3 Edición

1. El admin hace clic en “Editar” en una función no terminal.
2. La ruta busca la función en `GET /funciones/admin` por `id_funcion`.
3. Arma el borrador con fecha y hora separadas y abre el formulario precargado.
4. El admin modifica los campos permitidos.
5. El formulario envía `POST /admin/funciones/<id>/editar`.
6. El backend valida, recalcula `fin` si corresponde, controla solapamiento y entradas activas.
7. El frontend muestra flash de éxito y redirige al listado.
8. Si el backend rechaza (solapamiento, entradas vendidas, estado terminal), se muestra el mensaje y se conserva el borrador.

### 7.4 Baja

1. El admin hace clic en “Dar de baja” en una función no terminal.
2. Se abre el modal de confirmación con película, fecha y hora.
3. Al confirmar, se envía `POST /admin/funciones/<id>/eliminar`.
4. La ruta llama a `dar_de_baja_funcion(token, id)`.
5. El backend cancela lógicamente (`estado = 'CANCELADA'`) si no hay entradas activas.
6. El frontend muestra flash de éxito y redirige al listado.
7. La función sigue visible con badge “Cancelada” y sin acciones.

### 7.5 Funciones terminales

- `CANCELADA` y `FINALIZADA` se muestran en la tabla.
- No se muestran botones de edición ni baja.
- Si se intenta forzar la edición por URL, el backend responde 409 y el frontend muestra el error.

---

## 8. Seguridad y validaciones

| Riesgo | Control |
| :--- | :--- |
| Acceso de cliente a rutas admin | `@admin_required` en todas las rutas web; `validar_admin()` en todas las mutaciones del backend. |
| Manipulación de IDs desde el formulario | El backend valida existencia y estado activo de película y sala. |
| Solapamiento de horarios | `hay_solapamiento_horario_db()` dentro de la misma sala. |
| Cambios sobre funciones con entradas | `tiene_entradas_activas_db()` bloquea reprogramación y cancelación. |
| Inyección SQL | SQL parametrizado con `%s` en repositorios. |
| XSS en templates | Jinja2 autoescape; no se usa `|safe` con datos de usuario. |
| CSRF | El proyecto no tiene middleware CSRF global; se mantiene el patrón actual de formularios `POST` del frontend. No se introduce una dependencia nueva. |
| Hardcodeo de backend | `consultar_backend()` usa `BACKEND_URL` del `.env`. |
| Fechas inválidas | `validar_inicio_futuro()` en backend y `armar_inicio_iso()` en frontend. |

---

## 9. Casos borde y manejo

| Caso | Comportamiento esperado |
| :--- | :--- |
| Película inactiva en alta | Backend 400: “La película indicada no existe o está dada de baja.” |
| Sala inactiva en alta | Backend 400: “La sala indicada no existe o está deshabilitada.” |
| Inicio en el pasado | Backend 400: “El campo inicio debe ser una fecha y hora futura.” |
| Solapamiento en la misma sala | Backend 409: “La sala ya tiene una función asignada en esa franja horaria.” |
| Edición de función finalizada/cancelada | Backend 409: “No se puede modificar una función FINALIZADA/CANCELADA.” |
| Cambio de horario con entradas vendidas | Backend 409: “La función tiene entradas vendidas o reservadas.” |
| Baja de función con entradas vendidas | Backend 400: “No es posible dar de baja una función con entradas ya vendidas.” |
| Baja repetida | Backend 200 idempotente, mensaje de éxito. |
| Backend caído | `api_client` devuelve 502; el frontend muestra flash y no rompe. |
| Token vencido | Redirección al login y limpieza de sesión. |
| Listado vacío | Estado vacío “No hay funciones registradas”. |
| Sala actual inactiva en edición | Se muestra como opción marcada para no perder el dato; si se cambia a otra sala, se valida la nueva. |
| JS deshabilitado | El formulario funciona igual; el select de sala muestra todas las salas agrupadas. |

---

## 10. Pruebas y QA

### 10.1 Verificación de sintaxis

```bash
cd backend && .venv/bin/python -m compileall src app.py
cd ../frontend && .venv/bin/python -m compileall routes services utils app.py
```

### 10.2 Pruebas de backend con curl

```bash
# Login admin
TOKEN=$(curl -s -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@cineparadiso.com","password":"Admin1234!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Listado admin
curl -s http://127.0.0.1:5000/funciones/admin \
  -H "Authorization: Bearer $TOKEN"

# Alta
curl -s -X POST http://127.0.0.1:5000/funciones \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_pelicula": 1,
    "id_sala": 1,
    "inicio": "2026-12-01T20:00:00",
    "formato": "4D",
    "idioma": "Inglés",
    "subtitulada": true,
    "precio_entrada": 6500
  }'

# Edición completa
curl -s -X PUT http://127.0.0.1:5000/funciones/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_sala": 2,
    "inicio": "2026-12-02T21:00:00",
    "formato": "3D",
    "idioma": "Español",
    "subtitulada": false,
    "precio_entrada": 7000
  }'

# Baja
curl -s -X DELETE http://127.0.0.1:5000/funciones/1 \
  -H "Authorization: Bearer $TOKEN"
```

### 10.3 Pruebas de permisos

- Sin token:
  - `GET /funciones/admin` → 401.
  - `POST /funciones` → 401.
  - `PUT /funciones/1` → 401.
  - `DELETE /funciones/1` → 401.
- Con token de cliente:
  - los mismos endpoints → 403.
- `GET /funciones` y `GET /funciones/<id>/butacas` → 200 sin token.

### 10.4 Pruebas manuales de UI

1. `/admin/funciones` sin sesión → redirige al login/home.
2. `/admin/funciones` con cliente → acceso denegado.
3. `/admin/funciones` con admin → listado completo.
4. “+ Nueva función” → abre formulario y enfoca el primer campo.
5. Cambiar complejo → el select de sala se filtra.
6. Alta válida → flash de éxito y fila nueva.
7. Alta con solapamiento → flash de error y datos conservados.
8. Editar función programada → cambios persistidos.
9. Editar función finalizada/cancelada → no aparece el botón; por URL directa, error controlado.
10. Baja con modal → función queda “Cancelada” en la tabla.
11. Baja repetida → mensaje de éxito sin error.
12. Backend caído → flash de error, sin excepción 500 en el frontend.

### 10.5 Verificación en MySQL

```sql
USE proyecto_integrador;

SELECT id_funcion, id_pelicula, id_sala, inicio, fin, formato, idioma,
       subtitulada, precio_entrada, estado
FROM funciones
ORDER BY id_funcion;

SELECT COUNT(*) AS entradas_activas
FROM entradas
WHERE id_funcion = 1 AND estado IN ('OCUPADA', 'RESERVADA');
```

### 10.6 Registro de QA ejecutado

**Sintaxis y plantillas**

| Verificación | Resultado |
| :--- | :--- |
| `compileall` backend (`src` + `app.py`) | OK |
| `compileall` frontend (`routes`, `services`, `utils`, `app.py`) | OK |
| `node --check` de `modal.js`, `admin_funciones.js`, `admin_peliculas.js`, `admin_servicios.js` | OK |
| Compilación de todas las plantillas Jinja | OK |
| `git diff --check` | Sin errores de whitespace |

**Backend**

| Caso | Resultado esperado | Resultado |
| :--- | :--- | :--- |
| `GET /funciones/admin` con admin | 200 + listado completo | OK |
| `GET /funciones/admin` sin token | 401 | OK |
| `GET /funciones/admin` con cliente | 403 | OK |
| `POST`, `PUT`, `DELETE` sin token / con cliente | 401 / 403 | OK |
| Alta válida | 201 | OK |
| Edición completa (película, sala, inicio, formato, idioma, subtítulos, precio) | 200 + datos persistidos | OK |
| Edición solo de precio | 200 | OK |
| Solapamiento de sala | 409 | OK |
| Inicio en el pasado | 400 | OK |
| Película inexistente o inactiva | 400 | OK |
| Body vacío | 400 | OK |
| Modificación de función `CANCELADA` o `FINALIZADA` | 409 | OK |

**SSR / backoffice**

| Caso | Resultado |
| :--- | :--- |
| Listado con admin | 200, tabla completa con estados y acciones |
| Alta desde el formulario | Redirect + fila nueva |
| Edición desde el formulario | Redirect + cambios persistidos |
| Error de solapamiento | Re-render 200 conservando los datos ingresados |
| Baja con confirmación | Redirect + estado `CANCELADA` |
| Función terminal | Visible, sin botones de edición ni baja |
| Acceso desde dashboard | Botón “Gestionar funciones” presente |
| Cliente / sin sesión | Redirección o acceso denegado según `@admin_required` |

**Edición y casos borde**

| Caso | Resultado |
| :--- | :--- |
| Editar una función sin cambios | Flash “No se detectaron cambios en la función”, sin `PUT` |
| Editar una función `EN_CURSO` con segundos distintos de `00` y sin cambios | No se reenvía `inicio`; no aparece el error de fecha pasada |
| Editar solo el precio de una función `EN_CURSO` con inicio pasado | Precio actualizado correctamente |
| Cambiar el inicio de una función `EN_CURSO` a una fecha futura | Actualización correcta, sin solapamiento |
| `min` del input fecha en alta | Fecha actual |
| `min` del input fecha al editar una función `EN_CURSO` iniciada ayer | Fecha de inicio de la función |

**Modales y limpieza**

| Caso | Resultado |
| :--- | :--- |
| `modal.js` incluido en funciones, películas y servicios | OK |
| `data-confirmar-baja` y `data-modal-destino` presentes en las tres vistas | OK |
| Extracción desde `admin_peliculas.js` | Lógica idéntica; se eliminó el hook muerto `data-modal-pelicula` |
| Apertura, acción dinámica y cierre por “Cancelar” en funciones, películas y servicios | OK en Chrome headless |
| Modales de servicios fuera del `<tbody>` | Corregido; el formulario conserva sus botones |
| Referencias a `funciones_lista.html` / `funciones_form.html` | Ninguna |
| `backend/funciones_lista.html` | Eliminado |
| `fetch`, `axios`, AJAX, WebSockets | Ninguno |
| Clases / ORM | Ninguno |
| `requests` directo en rutas | Ninguno |

> La interacción real se verificó con **Chrome headless 157** controlado por **Chrome DevTools Protocol** desde Node 24 (WebSocket nativo): login por formulario, apertura/cierre de modales en los tres ABM, acción dinámica del formulario de baja, filtro complejo→sala y validez del input fecha. Las pruebas de rutas y formularios también se ejecutaron con sesiones HTTP reales contra los servidores locales.

> **Corrección detectada en la prueba de navegador:** en `servicios.html` los modales estaban dentro del `<tbody>`. El parser HTML cerraba el `<form>` antes de los botones y la confirmación de baja no podía enviarse. Se movieron fuera de la tabla, junto al resto del listado.

> Las funciones de prueba creadas para QA (ids 15, 16 y 21–24) se eliminaron al finalizar, dejando la tabla `funciones` en su estado inicial.

---

## 11. Criterios de aceptación

- [x] Existe `GET /funciones/admin` protegido con `validar_admin()`.
- [x] `POST`, `PUT` y `DELETE` de funciones exigen `ADMINISTRADOR`.
- [x] `PUT /funciones/<id>` acepta edición completa y mantiene las reglas de solapamiento y entradas.
- [x] El ABM lista funciones en todos los estados.
- [x] El formulario usa selects de película, complejo y sala; no pide IDs a mano.
- [x] El formulario separa fecha/hora en la UI y envía un único `inicio` ISO al backend.
- [x] La edición no usa `DELETE` + `POST`; usa `PUT`.
- [x] La baja es lógica (`CANCELADA`) y no borra la fila.
- [x] Todas las rutas usan `consultar_backend()`; no hay `requests` directo.
- [x] Todas las rutas web usan `@admin_required`.
- [x] Los formularios y tablas usan componentes reutilizables y `url_for()`.
- [x] No se agregaron dependencias ni cambios de esquema.
- [x] `swagger.yaml` documenta el endpoint admin y el `PUT` ampliado.
- [x] `compileall` pasa en backend y frontend.
- [x] No quedan `funciones_lista.html` ni `funciones_form.html` legacy.
- [x] El dashboard tiene acceso a “Gestionar funciones”.

---

## 12. Riesgos y mitigaciones

| Riesgo | Probabilidad | Mitigación |
| :--- | :--- | :--- |
| El modelo local (Ollama) introduce código fuera del patrón | Media | Ejecutar por fases, revisar `git diff` y aplicar el checklist de modularidad. |
| Romper el ABM de películas/servicios al extraer `modal.js` | Baja | Refactor pequeño y probar las tres páginas. |
| Cambiar el contrato de `PUT` y romper clientes existentes | Baja | Todos los campos nuevos son opcionales; los campos actuales siguen funcionando. |
| Solapamiento por cálculo de `fin` incorrecto | Media | Reutilizar `_calcular_fin` y probar con películas de distinta duración. |
| Editar una función con entradas activas | Media | Bloqueo explícito en servicio y prueba con entradas `OCUPADA`/`RESERVADA`. |
| `GET /funciones/admin` demasiado grande | Baja | El volumen del proyecto es acotado; si crece, se agregan filtros en otra tarea. |
| El JS de filtrado local→sala no funciona sin JS | Baja | El select de sala siempre contiene todas las salas agrupadas; el formulario sigue siendo usable. |

---

## 13. Orden de commits sugerido

La implementación quedó sin commitear sobre `develop`. Antes de commitear, crear una rama de trabajo:

```bash
git switch -c feature/admin-funciones

# 1. Backend
git add backend/src/repositories/funciones_repository.py \
        backend/src/services/funciones_services.py \
        backend/src/validators/funciones_validators.py \
        backend/src/routes/funciones_routes.py \
        docs/swagger.yaml
git commit -m "[FUNCIONES] Agrega listado admin y edición completa de funciones (#Tarea2)"

# 2. Frontend: servicios, utilidades y rutas
git add frontend/services/admin_funciones_service.py \
        frontend/utils/funciones.py \
        frontend/routes/admin_funciones_routes.py
git commit -m "[FUNCIONES] Implementa ABM SSR de funciones en el backoffice (#Tarea2)"

# 3. Frontend: vistas, componentes, CSS y JS
git add frontend/templates/backoffice/funciones.html \
        frontend/templates/components/formulario_funcion.html \
        frontend/templates/components/modal_confirmacion.html \
        frontend/templates/backoffice/dashboard.html \
        frontend/templates/backoffice/peliculas.html \
        frontend/templates/backoffice/servicios.html \
        frontend/static/css/pages/admin_funciones.css \
        frontend/static/js/admin_funciones.js \
        frontend/static/js/modal.js \
        frontend/static/js/admin_peliculas.js
git commit -m "[FUNCIONES] Agrega vista, formulario, modales y estilos del ABM (#Tarea2)"

# 4. Limpieza y documentación
git add docs/tasks/tarea_u_funciones.md
git rm frontend/templates/backoffice/funciones_lista.html \
       frontend/templates/backoffice/funciones_form.html \
       backend/funciones_lista.html
git commit -m "[FUNCIONES] Limpia plantillas legacy y documenta el plan (#Tarea2)"
```

> No hacer commit ni push sobre `main` o `develop`. Abrir Pull Request hacia `develop`.

---

## 14. Resumen de archivos

### Nuevos

- `frontend/services/admin_funciones_service.py`
- `frontend/utils/funciones.py`
- `frontend/templates/backoffice/funciones.html`
- `frontend/templates/components/formulario_funcion.html`
- `frontend/static/css/pages/admin_funciones.css`
- `frontend/static/js/admin_funciones.js`
- `frontend/static/js/modal.js`
- `docs/tasks/tarea_u_funciones.md`

### Modificados

- `backend/src/repositories/funciones_repository.py`
- `backend/src/services/funciones_services.py`
- `backend/src/validators/funciones_validators.py`
- `backend/src/routes/funciones_routes.py`
- `docs/swagger.yaml`
- `frontend/routes/admin_funciones_routes.py` (reescritura completa)
- `frontend/templates/backoffice/dashboard.html` (acceso a “Gestionar funciones”)
- `frontend/templates/backoffice/peliculas.html` (incluye `modal.js`; quita atributo muerto)
- `frontend/templates/backoffice/servicios.html` (incluye `modal.js`; mueve los modales fuera del `<tbody>`)
- `frontend/templates/components/modal_confirmacion.html` (corrige `variante` de los botones)
- `frontend/static/js/admin_peliculas.js` (elimina lógica duplicada de modales)

### Eliminados

- `frontend/templates/backoffice/funciones_lista.html`
- `frontend/templates/backoffice/funciones_form.html`
- `backend/funciones_lista.html`

### Sin cambios

- `backend/db/init_db.sql` y `seed_data.sql`
- `backend/requirements.txt` y `frontend/requirements.txt`
- `frontend/services/funciones_service.py` (cliente público)
- `frontend/static/js/admin_servicios.js` (no necesitó cambios)
- `frontend/app.py` (el blueprint ya estaba registrado)
- `frontend/templates/components/button.html`
- `frontend/templates/components/campo_formulario.html`
- `frontend/static/css/components/modal.css`
- `frontend/templates/components/navbar.html` (Tarea 11)

---

## 15. Orquestación y resultado real

El plan se usó como contrato y la implementación se dividió en tres entregas (backend; servicios/utilidades/rutas; vistas/CSS/JS), cada una seguida de revisión humana y correcciones.

### 15.1 Intento con Codex + Ollama (fallido)

- **Herramienta:** Codex CLI con proveedor `ollama-launch`.
- **Modelos probados:**
  - `qwen2.5-coder:7b`: no ejecutó de forma confiable las herramientas de Codex; las ediciones quedaban incompletas o fuera del alcance.
  - `gpt-oss:20b`: pérdida de conexión durante las sesiones.
- **Conclusión:** no fue confiable para un flujo multiarchivo con herramientas. Se descartó como obrero principal.

### 15.2 Suplente real: Gemini CLI

- **Comando:** `gemini -m gemini-3.1-flash-lite --approval-mode yolo --skip-trust -p "..."`
- Se usó para implementar las fases 2–5.
- **Limitaciones:** cuota gratuita, reintentos y logs que pueden mostrar otro identificador de modelo (`gemini-3.5-flash-lite`).
- Cada entrega se revisó y corrigió manualmente. Los ajustes principales fueron:
  - `_payload_actualizacion()` + `_normalizar_inicio()` para no reenviar un `inicio` pasado.
  - `fecha_minima` dinámica al editar funciones `EN_CURSO`.
  - Limpieza del hook muerto de películas en `modal.js`.
  - Corrección de `variante` en `modal_confirmacion.html`.
  - Eliminación de plantillas legacy y verificación de referencias.
  - Reversión de un cambio fuera de alcance en `obtener_estado_butacas_funcion_db`.

### 15.3 Lecciones

- El modelo local no reemplaza la revisión humana en tareas con muchos archivos y contratos estrictos.
- Gemini CLI sirve como suplente, pero la cuota y los reintentos obligan a dividir el trabajo en fases pequeñas.
- El plan y el `git diff` fueron la fuente de verdad para aceptar o corregir cada entrega.

Cada fase debe terminar con revisión humana del `git diff` y de los criterios de aceptación.

---

## 16. Próximo paso

1. [x] Aprobar este plan.
2. [x] Implementar la Fase 1 (backend).
3. [x] Implementar Fases 2–5 (frontend).
4. [x] Ejecutar QA y revisar el diff completo.
5. [x] Responder las dos preguntas de validación oral de la skill 04.
6. [x] Crear `feature/admin-funciones` y commitear por etapas.
7. [ ] Subir la rama y abrir Pull Request hacia `develop`.
