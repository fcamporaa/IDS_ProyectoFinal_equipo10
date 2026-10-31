# US-09 · Envío de QR por mail — plan, ejecución y trazabilidad

## 1. Rama sugerida
`feature/us-09-envio-qr-mail` desde `develop`. **El ZIP no crea commits ni modifica tu repositorio Git**. Trabajá por rama y solicitá revisión antes de fusionar.

## 2. Auditoría de reutilización

Instrucciones leídas: `AGENTS.md`, `GEMINI.md`, las cuatro skills de `.agents/skills/` y `docs/plan_templates_frontend.md`.

- Reutilizado: `backend/src/db.py` (`obtener_conexion`, `ejecutar_consulta`), `backend/src/utils.py` (`construir_error_api`), constantes de `src/constants.py`, Blueprint existente de `frontend/routes/home_routes.py`, layout Jinja existente y paleta CSS actual.
- Respetado: *routes* solo HTTP, *validators* validación, *services* reglas y correo, *repositories* SQL con `%s`; SSR y `requests` en Python sin `fetch`/AJAX; Jinja `url_for`; HTML reutilizable en componentes.
- Activos generales nuevos: `src/utils.enviar_correo_html(destinatario, asunto, plantilla, contexto, imagenes_inline)`, `src.utils.renderizar_correo_html()`, `frontend/templates/components/` para input/botón/mensajes; `src/config.py` para configuración de ejecución.
- **Limitación de aprobación humana:** la petición de crear el ZIP autoriza elaborar esta propuesta; no equivale a una revisión oral ni a aprobación de un PR. No se ejecutaron commits.
- **Dependencias:** no se modificó NINGÚN `requirements.txt`: el frontend requiere `requests` y la imagen QR requiere `qrcode` (con Pillow); antes de añadirlos al manifiesto pedí aprobación explícita al equipo, como exige `AGENTS.md`.

## 3. Plan paso a paso por archivo (en el mismo orden de la imagen)

### Paso 1 · `frontend/templates/client/checkout.html`
Formulario **provisorio** solamente para integración con US-08. Extiende `layout.html`, incluye componentes `campo_formulario.html`, `boton.html`, `mensajes.html` y envía `POST` a `url_for('compras.confirmar_compra')`. Tiene token CSRF. No procesa tarjetas reales ni sustituye la maqueta final de US-08.

### Paso 2 · `frontend/routes/compras_routes.py` → `frontend/services/compras_service.py`
El Blueprint se registra en `frontend/app.py`. `confirmar_compra()` recibe `request.form` y valida el CSRF en `frontend/utils/csrf.py`; `frontend/validators/compras_validators.py` convierte los identificadores y valida campos; `enviar_compra_al_backend()` envía JSON mediante `requests.post()` con `Authorization: Bearer ...`. La autenticación de cliente será suministrada por US-02.

### Paso 3 · `backend/src/routes/compras_routes.py`
Se convirtió la sección de compras a Blueprint registrado desde `backend/app.py`. `post_compra()` obtiene credencial firmada, invoca el validador del JSON y delega a `procesar_compra()`. `GET /compras/{id}` valida titularidad; `POST /compras/{id}/reenviar-comprobante` exige autenticación. Documentado en `docs/swagger.yaml`. Las demás rutas de compras no se implementan fuera de alcance.

### Paso 4 · `backend/src/validators/compras_validators.py` y `backend/src/services/compras_services.py`
Validación de tipos, rangos, IDs, butacas no repetidas y email. Solo `TARJETA_SIMULADA` y solo si `ALLOW_SIMULATED_PAYMENTS=true` (desactivado por defecto). **No hay validación bancaria real.** `procesar_compra()` genera código de reserva y token opaco, pide guardar compra y luego solicita el correo.

### Paso 5 · `backend/src/repositories/compras_repository.py` y MySQL
`registrar_compra_pagada_db()` abre transacción, bloquea la función con `FOR UPDATE`, comprueba disponibilidad, calcula importes con precios de BD, inserta `compras`, `entradas`, `compra_servicios` y hace `COMMIT` o `ROLLBACK`. Se agregaron índices `UNIQUE` para QR/reserva y columna generada para impedir dos entradas activas por butaca/función. El `init_db.sql` aplica en bases nuevas. Para bases existentes: **respaldar primero y ejecutar UNA vez** `backend/db/migrations/001_us09_qr_correo.sql`. La migración puede fallar si hay duplicados previos; detectarlos antes.

### Paso 6 · `backend/src/services/comprobantes_services.py`, `qr_services.py`, `backend/src/utils.py`
`enviar_comprobante_compra(id_compra, plantilla)` consulta el registro ya confirmado; para `compra_confirmada`, prepara QR PNG y pasa `imagen_inline` a la función **genérica** `enviar_correo_html()`, que renderiza `backend/src/templates/emails/compra_confirmada.html` con Jinja escapando HTML. Para `comprobante_provisorio` no genera QR; US-19 puede reutilizar la misma función cuando exista la reserva `PENDIENTE`. `EMAIL_MODE=console` no envía nada; `smtp` usa servidor configurado. Los fallos se registran en `compras.email_estado` sin revertir la transacción pagada.

### Paso 7 · `frontend/templates/client/compra_exitosa.html`
La ruta frontend redirige tras recibir `201`, consulta `GET /compras/{id}`, comprueba titularidad en el backend y renderiza detalles y `email_estado`. La página **no reenvía automáticamente** al actualizar. Reenvío explícito por `POST` con CSRF.

## 4. Preguntas de revisión para defensa oral

1. ¿Por qué `registrar_compra_pagada_db` usa `FOR UPDATE` y `UNIQUE`, además de `COMMIT` y `ROLLBACK`?
2. ¿Por qué `enviar_correo_html` se llama **después** del `COMMIT`, y por qué cambiar la plantilla permite reutilizar la función en US-19?

## 5. Integraciones y límites de esta versión

- **US-02 aún no implementada:** el frontend requiere `session['access_token']`; el backend verifica una credencial firmada mediante `src/services/sesion_services.py`. `emitir_token_sesion()` debe integrarse al login **solo después de verificar las credenciales**. No se habilitó ningún usuario ficticio ni autenticación por ID enviado en el JSON.
- **US-08 aún no implementada:** checkout definitivo, tarjeta real, medio efectivo, UI de selección de butacas y facturación fiscal quedan fuera de este alcance. Para demostrar la integración, hay un formulario técnico mínimo y modo de pago **simulado**. `PAGADA` aquí significa compra simulada confirmada, **no una transacción bancaria**.
- **US-14 aún no implementada:** el QR identifica una compra, pero el endpoint `/validaciones-qr` original sigue pendiente. Una compra de varias entradas usa un único QR grupal por esquema actual.
- **Correo real:** configurar variables SMTP; sin ellas `EMAIL_MODE=console` solo marca el intento `SIMULADO`. QR requiere paquete `qrcode` disponible en el entorno; no está declarado en `requirements.txt` por restricción de aprobación previa.
- **Email HTML ≠ factura fiscal válida.** La plantilla se declara demostrativa; no se integra un facturador electrónico.
- **Pruebas:** `python -m pytest tests/test_us09.py` con pytest y las dependencias de desarrollo disponibles. La prueba SQL end-to-end requiere MariaDB/MySQL real; no se ejecutó en este entorno.
- **Servidor frontend:** configurar `SECRET_KEY` segura >=32 caracteres; servidor backend: `AUTH_SECRET_KEY` >=32, `ALLOW_SIMULATED_PAYMENTS=true` solamente en desarrollo. Para usar ambos servicios también es necesaria la URL `BACKEND_URL`.
- **Versionado:** no incluir `.env`, `.venv`, `venv` ni cachés Python en Git.

## 6. Revisión previa al PR

1. Revisar las consultas en MySQL de prueba y migración sobre copia respaldada.
2. Obtener autorización de dependencias antes de editar los `requirements.txt`; ejecutar `backend/init.sh` y reinstalar frontend.
3. Integrar US-02 y hacer prueba completa frontend→backend→MySQL→SMTP.
4. Revisar que el equipo no haya implementado cambios paralelos en US-07 y US-08 antes de fusionar.
5. Una vez comprendido y aprobado el código, usar `git add` solo de los archivos correspondientes, `git commit -m "[US-09] Integra QR y envío de correo (#72 #73 #75)"` y `git push origin feature/us-09-envio-qr-mail`; abrir PR hacia `develop`.
