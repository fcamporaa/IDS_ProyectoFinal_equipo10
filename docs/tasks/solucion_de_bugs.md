# Solución de bugs — Flujo de compra (`/compra/*`)

- **Fecha de análisis:** 2026-11-18
- **Alcance:** Issues reportados en el embudo de compra (selección de servicios, checkout y confirmación de pago simulado).
- **Estado:** Análisis y plan de implementación (sin cambios de código aplicados en este documento).
- **Restricciones del proyecto:** SSR con Flask + Jinja2, sin `fetch`/AJAX/WebSockets; backend en 4 capas (`routes -> validators -> services -> repositories`); sin ORM/clases; no agregar dependencias sin autorización explícita.

## 1. Contexto y metodología de prueba

### 1.1 Entorno observado
- Frontend activo en `http://127.0.0.1:5001` (Flask debug, `frontend/.venv`).
- Backend activo en `http://127.0.0.1:5000` (Flask debug, `backend/.venv`).
- Base de datos usada por el backend en ejecución: MySQL local `127.0.0.1:3306` (`proyecto_integrador`, según `backend/.env`).
- También existe contenedor Docker `cine_paradiso_db` expuesto en `3307` (esquema/semilla distintos al de la BD en uso). **Hay deriva de esquema entre BDs y respecto de `backend/db/init_db.sql`** (ver hallazgos).

### 1.2 Pruebas realizadas (reproducibles)
1. Registro y login de usuario cliente vía backend/frontend (`/auth/register`, `/auth/login`).
2. Flujo SSR de compra sobre la función vigente `id_funcion=25` (Oppenheimer, Sala 1, 4D, `precio_entrada=1212.00`, 1 butaca seleccionada `A-1`).
3. Inspección de `GET /compra/servicios`, `POST /compra/servicios` (`accion=continuar` y `accion=omitir`), `GET /compra/checkout`, `POST /compra/confirmar`.
4. Prueba directa de `POST /compras` en backend con token Bearer del cliente.
5. Verificación de endpoints/BD: `GET /servicios` (backend), `SHOW COLUMNS FROM servicios`, consulta de función/película/sala.

### 1.3 Evidencia resumida
| Prueba | Resultado observado |
|---|---|
| `GET /compra/servicios` (función 25, 1 entrada A-1, $1.212) | Muestra **“Furiosa: Saga Mad Max”**, **“Butacas E-08, E-09”**, **“$17.000”**; no muestra Oppenheimer ni el monto real. |
| `POST /compra/servicios` con `servicios_json=[]`, `accion=continuar` | Respuesta `200` en `http://127.0.0.1:5001/compra/servicios` (permanece en la pantalla, no avanza). |
| `POST /compra/servicios` con `servicios_json=[]`, `accion=omitir` | Respuesta `200` tras redirect a `http://127.0.0.1:5001/compra/checkout` (flujo continúa). |
| `GET /servicios` (backend) | `500` con error interno (`OperationalError 1054: Unknown column 'imagen_url' in 'field list'`). |
| `GET /compra/checkout` (tras omitir) | Carga correcto: película Oppenheimer, total `$1.212`, `action` del form `/compra/confirmar`. |
| `POST /compra/confirmar` (datos válidos, Luhn/DNI/email OK) | Vuelve a checkout con mensaje “No se pudo confirmar la compra…”. |
| `POST /compras` (backend, payload válido, token cliente) | `501` → `{"code":"compras.pago","message":"Pago no disponible","description":"Habilitá ALLOW_SIMULATED_PAYMENTS solo en desarrollo."}` |
| Compra con `ALLOW_SIMULATED_PAYMENTS=true` (prueba controlada en proceso) | `procesar_compra` registra compra `PAGADA`, persiste entradas/servicios y totales correctos (luego se revirtió la prueba). |

---

## 2. Hallazgos por issue

### Issue 1 — No coincide la película ni el monto en `/compra/servicios`

**Síntoma reportado:** en Servicios Extras se muestra otra película y un monto distinto al de la compra en curso.

**Reproducción:**
1. Seleccionar función 25 (Oppenheimer) y 1 butaca.
2. Continuar a `/compra/servicios`.
3. Observar encabezado/resumen lateral.

**Resultado observado:** datos hardcodeados de “Furiosa…” (Sala 2 • 4D, butacas E-08/E-09, subtotal entradas $17.000) en lugar de los datos reales de la sesión (Oppenheimer, A-1, $1.212).

**Causa raíz (frontend):** la vista de servicios no consume el estado real de la compra.
- `frontend/routes/compra_routes.py` → `seleccion_servicios()` (GET): construye `datos_compra` con valores fijos (`subtotal_entradas = 17000`, película “Furiosa…”, items/butacas/poster/formato/horario/sede hardcodeados) y no deriva la información desde `session["compra"]`.
- El guardado correcto de la selección real sí ocurre en `seleccion_butacas()` (`session["compra"]` incluye `id_funcion`, `id_pelicula`, `pelicula_titulo`, `complejo`, `sala_*`, `horario`, `precio_unitario`, `butacas`, `subtotal_entradas`, etc.), y `seleccion_checkout()` sí la utiliza; la ruptura está aislada en la etapa de servicios.

**Archivos involucrados:**
- `frontend/routes/compra_routes.py` (`seleccion_servicios`, armado de `datos_compra`).
- `frontend/templates/seleccion_servicios.html` (render de resumen/película/entradas).
- `frontend/static/js/seleccion_servicios.js` (usa `data-subtotal-entradas` del DOM; depende de que el subtotal sea real).
- (Apoyo/reutilización) `frontend/services/peliculas_service.py`, `frontend/utils/formatos.py` para enriquecer poster/clasificación/horario si se requiere paridad visual con checkout.

**Impacto:** inconsistencia funcional y de confianza en el embudo; el usuario ve importes y función incorrectos antes de pagar.

---

### Issue 2 — “Continuar al pago” no avanza sin servicios; botón duplicado y backend 500 en el flujo

**Síntoma reportado:**
- “Continuar al pago” en `/compra/servicios` no funciona si no se selecciona nada (solo funciona “Omitir este paso…”).
- En el intento, el backend devuelve error 500.
- Se solicita quitar “Omitir este paso…” y unificar en “Continuar al pago” (con o sin ítems).

**Reproducción:**
1. Llegar a `/compra/servicios` con butacas seleccionadas.
2. No elegir servicios y presionar “CONTINUAR AL PAGO”.
3. Observar que permanece en `/compra/servicios`; repetir con “Omitir…” y avanza a checkout.

**Resultado observado:** `POST /compra/servicios` (`accion=continuar`) → 200 en la misma URL (sin avance). `accion=omitir` → redirect a checkout. En paralelo, `GET /servicios` del backend responde 500.

**Causa raíz (mixta frontend + estado del backend/BD):**
- **Frontend (`seleccion_servicios` POST):**
  - La ruta trata `accion=omitir` como camino rápido (vacía servicios y redirige) pero para `continuar` siempre: valida `servicios_json`, consulta el catálogo (`obtener_servicios_disponibles()` → `GET /servicios`) y, si `catalogo is None`, muestra “No se pudo validar el catálogo de servicios.” y redirige de vuelta. Esto impide avanzar incluso con selección vacía cuando el catálogo no está disponible.
  - Existen dos acciones/botones que duplican comportamiento según el caso (`accion=continuar` y `accion=omitir`, más enlace secundario inferior).
- **Backend/BD (origen del 500 observado):** `GET /servicios` falla en la BD en uso (`127.0.0.1:3306`) por deriva de esquema: el repositorio/servicio consulta la columna `imagen_url` (`backend/src/repositories/servicios_repository.py`, `SELECT ... imagen_url FROM servicios`), pero la tabla `servicios` en esa BD **no tiene** `imagen_url` (y además difiere en el `ENUM` de `tipo` respecto de `init_db.sql`). El error propagado es `OperationalError (1054, "Unknown column 'imagen_url' in 'field list'")`, que el manejador global devuelve como 500. Nota: `init_db.sql` ya define `imagen_url`, por lo que una BD inicializada con el esquema actual no presentaría esta columna faltante; el entorno activo está desalineado.

**Archivos involucrados:**
- `frontend/routes/compra_routes.py` (`seleccion_servicios` POST: ramas `omitir`/`continuar`, validación de catálogo).
- `frontend/services/servicios_service.py` (`obtener_servicios_disponibles`, adaptación; depende de `GET /servicios`).
- `frontend/templates/seleccion_servicios.html` (botón principal “CONTINUAR AL PAGO”, botón/enlace “Omitir este paso…”).
- `frontend/static/js/seleccion_servicios.js` (serializa `servicios_json` al enviar).
- `backend/src/repositories/servicios_repository.py`, `backend/src/services/servicios_services.py`, `backend/src/routes/servicios_routes.py` (consulta de `imagen_url`).
- `backend/db/init_db.sql` y esquema real de la BD en uso (alineación/migración).

**Impacto:** bloqueo del avance a checkout sin extras en entornos con catálogo no disponible; UX confusa por acciones duplicadas.

---

### Issue 3 — Checkout/pago no permite confirmar (error 501 en backend)

**Síntoma reportado:** no se puede llegar a la confirmación desde `/compra/checkout`; al probar datos ficticios que pasan Luhn, el backend responde 501.

**Reproducción:**
1. Completar butacas y servicios (u omitir) hasta llegar a `/compra/checkout` con datos reales de sesión.
2. Completar formulario con datos válidos (tarjeta con Luhn válido, MM/AA vigente, CVV, DNI, emails coincidentes) y enviar.
3. Observar que no se genera la confirmación.

**Resultado observado:**
- `POST /compra/confirmar` (frontend) → regresa a checkout con “No se pudo confirmar la compra. Revisá la función, las butacas y la sesión.”
- `POST /compras` (backend, mismo payload lógico) → `501 Not Implemented` con `code=compras.pago`: “Pago no disponible. Habilitá ALLOW_SIMULATED_PAYMENTS solo en desarrollo.”

**Causa raíz (backend, configuración de entorno):**
- `backend/src/config.py` → `pagos_simulados_habilitados()` lee `ALLOW_SIMULATED_PAYMENTS` (default `false`).
- `backend/src/services/compras_services.py` → `procesar_compra()` bloquea la operación si el flag no está habilitado y lanza error de negocio con `HTTP_NO_IMPLEMENTADO` (501).
- `backend/.env` no habilita pagos simulados; por eso el flujo de compra demostrativa no puede completarse aunque la validación del formulario sea correcta. (Validado: con el flag habilitado, la lógica de registro/persistencia funciona correctamente.)

**Archivos involucrados:**
- `backend/src/config.py`, `backend/src/services/compras_services.py`, `backend/src/constants.py` (`HTTP_NO_IMPLEMENTADO`).
- `backend/.env`, `backend/.env.example` (documentación/configuración del flag).
- `frontend/routes/compras_routes.py` (`confirmar_compra`: mapeo genérico de error; no expone el motivo real del 501).
- `frontend/services/compras_service.py`, `frontend/validators/compras_validators.py` (payload/validación previa).
- (Dependencia de la pantalla de éxito) `frontend/routes/compras_routes.py` (`compra_exitosa`, usa `qrcode` para generar QR en memoria).

**Impacto:** imposibilidad de completar el checkout en el entorno actual; el mensaje genérico dificulta el diagnóstico para el usuario.

---

## 3. Plan de acción e implementación

> Orden sugerido: primero desbloquear confirmación y catálogo (P0), luego corregir coherencia de datos/UI del embudo (P0/P1). Respetar arquitectura por capas y reutilizar utilidades existentes (`utils.formatos`, `services.*`, validadores actuales).

### 3.1 P0 — Habilitar compra simulada y mejorar diagnóstico (Issue 3)

**Objetivo:** permitir completar una compra de desarrollo y mostrar un error claro cuando el pago simulado esté deshabilitado.

**Acciones:**
1. **Configuración (entorno):** definir `ALLOW_SIMULATED_PAYMENTS=true` en `backend/.env` para desarrollo local (mantener `false` por defecto en entornos no demo, según política). Reiniciar el proceso del backend para que tome la variable.
2. **Backend:** sin cambios de lógica de negocio requeridos si el flag se configura; verificar que `EMAIL_MODE` y dependencias de comprobante no bloqueen el commit (el servicio ya tolera fallo de envío marcando estado de email). Opcional: documentar en README/guía operativa el prerequisito de pagos simulados.
3. **Frontend (`compras_routes.confirmar_compra`):** ante respuesta no 201, propagar el mensaje descriptivo del backend cuando exista (`errors[0].description`/`message` o `error/mensaje`) en el `flash`, manteniendo un fallback genérico. Esto hace visible el 501/configuración y otros rechazos (función no disponible, butaca ocupada, etc.).
4. **Verificación de dependencias de éxito:** confirmar que `qrcode[pil]` esté instalado en `frontend/.venv` (está en `frontend/requirements.txt`) para renderizar `/compras/<id>/confirmacion`.

**Criterios de aceptación:**
- Con `ALLOW_SIMULATED_PAYMENTS=true` y datos válidos, `POST /compra/confirmar` redirige a la pantalla de confirmación con compra `PAGADA`.
- Con el flag deshabilitado, el usuario ve un mensaje explícito indicando que el pago simulado no está habilitado.

### 3.2 P0 — Alinear catálogo de servicios y robustecer el paso de extras (Issue 2)

**Objetivo:** que “Continuar al pago” funcione con o sin servicios y eliminar la ambigüedad de botones, aun si el catálogo presenta fallas recuperables.

**Acciones:**
1. **Base de datos / esquema (entorno y consistencia):**
   - Alinear la BD en uso con el modelo esperado por el código: asegurar columna `imagen_url` en `servicios` (y tipos/constraints coherentes con `backend/db/init_db.sql` y validadores actuales). 
   - Si se usa la BD local existente, aplicar migración manual controlada (p.ej. `ALTER TABLE servicios ADD COLUMN imagen_url TEXT DEFAULT NULL` donde falte) y revisar compatibilidad de `tipo`. Si se usa Docker, recrear/inicializar con `init_db.sql`/`seed_data.sql` vigentes.
   - Validar que `GET /servicios` responda 200 antes de probar el flujo completo.
2. **Frontend — ruta (`frontend/routes/compra_routes.py`, `seleccion_servicios` POST):**
   - Unificar la lógica en una sola acción de continuación: parsear/validar `servicios_json` (permitir lista vacía) y, **solo si hay ítems seleccionados**, obtener y validar contra el catálogo activo; si la selección es vacía, persistir `[]` y avanzar sin depender de la consulta al catálogo.
   - Mantener validaciones de CSRF, de estructura/cantidades (validator existente) y de pertenencia de IDs al catálogo cuando aplique.
   - Conservar mensajes de error específicos (catálogo no disponible cuando sí se requieren servicios, servicio inexistente/inactivo, etc.).
3. **Frontend — template (`seleccion_servicios.html`):**
   - Eliminar los controles “Omitir este paso / Omitir este paso y pagar entradas” (header y pie del resumen).
   - Dejar un único CTA principal “CONTINUAR AL PAGO” que envíe la selección actual (vacía o no). Ajustar textos auxiliares si es necesario para no implicar obligatoriedad de extras.
4. **Frontend — JS (`seleccion_servicios.js`):**
   - Verificar que el submit serialice correctamente `servicios_json` con los ítems de cantidad > 0 (comportamiento actual) y que funcione con el botón unificado.

**Criterios de aceptación:**
- Con 0 servicios seleccionados, “Continuar al pago” lleva a `/compra/checkout`.
- Con servicios seleccionados, se validan contra catálogo, se guardan en sesión y se reflejan en checkout.
- No existe el botón/enlace de omitir; el flujo queda unificado.
- `GET /servicios` funciona con el esquema de BD alineado (sin 500 por columna faltante).

### 3.3 P0 — Corregir datos reales de la compra en Servicios (Issue 1)

**Objetivo:** mostrar en `/compra/servicios` la película, función, butacas y montos correspondientes a la selección real.

**Acciones:**
1. **Fuente de verdad:** en `seleccion_servicios()` (GET y, si se re-renderiza en error, POST), leer `session["compra"]` (validando presencia de `butacas`/`id_funcion`, como ya se hace parcialmente) y construir el contexto a partir de ella:
   - Entradas: cantidad, etiquetas de butacas (`fila-numero`), subtotal = `subtotal_entradas` (o `precio_unitario * cantidad`).
   - Película/función: `pelicula_titulo`, `id_pelicula`, `complejo`, `sala_completa/sala_numero`, `horario`, `formato/idioma` según disponibilidad.
2. **Enriquecimiento (reutilización):** reutilizar `obtener_detalle_pelicula`, `obtener_detalle_funcion_del_backend` y/o `utils.formatos` para poster, clasificación, idioma/subtitulado y formato legible de fecha/hora (paridad con `seleccion_checkout`/butacas), con fallbacks seguros si falta algún dato.
3. **Resumen económico:** eliminar constantes hardcodeadas (17000, “Furiosa”, etc.). Calcular `subtotal_candy` desde el catálogo/cantidades en sesión y `total = subtotal_entradas + subtotal_candy`; exponer `entradas.subtotal` y totales formateados coherentes para la plantilla y para `data-subtotal-entradas` usado por JS.
4. **Plantilla/JS:** ajustar bindings solo si cambian nombres de campos; mantener el contrato actual del payload (`id_servicio`, `cantidad`) y del contador/total dinámico.

**Criterios de aceptación:**
- La pantalla de servicios refleja la misma película, función, butacas y subtotal de entradas que butacas/checkout.
- Al agregar/quitar extras, el total acumulado se actualiza sobre el subtotal real.
- No quedan datos hardcodeados de otra película.

### 3.4 P1 — Consistencia, pruebas y documentación

**Acciones:**
1. **Pruebas manuales end-to-end:** butacas → servicios (con y sin extras) → checkout → confirmación → pantalla de éxito; verificar totales, persistencia en sesión, QR y detalle.
2. **Casos borde:** temporizador vencido, CSRF inválido, servicio desactivado durante el flujo, butaca ocupada al confirmar (409), reintento tras error de confirmación.
3. **Documentación operativa:** actualizar notas de setup (`README.md` o guía correspondiente) indicando `ALLOW_SIMULATED_PAYMENTS`, alineación de esquema/BD y dependencias del frontend (`qrcode[pil]`).
4. **Limpieza de datos de prueba:** eliminar usuarios/compras generados durante pruebas si corresponde.

## 4. Riesgos y notas

- **Deriva de BD:** el entorno probado tiene diferencias relevantes (columna `imagen_url` ausente en `servicios`, variaciones de `tipo`/datos de usuarios/funciones). Sin alineación, pueden persistir 500 o comportamientos inconsistentes entre entornos.
- **Mensajes al usuario:** el frontend hoy oculta causas concretas del fallo de compra; exponer la descripción del backend mejora soporte pero debe evitar filtrar detalles sensibles.
- **Concurrencia:** la disponibilidad real de butacas se valida en backend al confirmar; mantener el flujo SSR sin asumir reserva definitiva hasta el pago/registro.
- **Dependencias:** `qrcode[pil]` es necesaria para la confirmación visual del QR; ya está declarada, pero debe estar instalada en el entorno de ejecución.

## 5. Resumen ejecutivo

| Issue | Causa principal | Tipo | Acción clave |
|---|---|---|---|
| 1. Película/monto incorrectos en servicios | Contexto hardcodeado en `seleccion_servicios` (no usa `session["compra"]`) | Frontend | Construir vista desde sesión real + enriquecimiento reutilizable |
| 2. “Continuar al pago” falla sin extras / duplicidad de botones / 500 | Validación acoplada a catálogo incluso vacío + catálogo cae por esquema BD desalineado (`imagen_url`) + UI con dos acciones | Frontend + BD/entorno | Unificar CTA, permitir continuar sin extras sin depender de catálogo vacío, alinear esquema y validar solo selección > 0 |
| 3. Checkout no confirma (501) | `ALLOW_SIMULATED_PAYMENTS` deshabilitado en backend | Config backend + manejo de error frontend | Habilitar flag en dev, reiniciar backend y mostrar mensaje de error real |

**Definición de terminado:** flujo completo de compra funcional en entorno de desarrollo (con pagos simulados habilitados y BD alineada), datos coherentes en cada paso, un solo botón de continuación en servicios y mensajes de error informativos ante fallos de confirmación.
