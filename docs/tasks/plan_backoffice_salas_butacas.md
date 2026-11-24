# Plan de implementación — Backoffice de salas y butacas

## Objetivo
Permitir que un administrador cree una sala con su grilla de butacas desde el backoffice, sin carga manual en la base de datos, y corregir la ausencia de butacas en Palermo/Belgrano al comprar.

## Diagnóstico actual
- Backend (`salas_routes`, `salas_services`, `salas_repository`) solo lista y actualiza salas; no hay alta ni generación de butacas.
- Butacas se insertan manualmente en `backend/db/seed_data.sql`.
- Frontend no tiene módulo `admin_salas`.
- Belgrano no existe en BD (solo Centro y Palermo).
- Palermo tiene sala 3 y butacas 27-34, pero la función 4 no tiene `entradas` en seed.

## Fase 1 — Backend: alta de sala
1. Agregar `POST /locales/<int:id_local>/salas` (admin) en `salas_routes.py`.
2. Validar local existente y número de sala único por local.
3. Implementar `insertar_sala_db` en `salas_repository.py`.
4. Servicio `crear_sala` en `salas_services.py`.

## Fase 2 — Backend: generación de butacas
1. Endpoint `POST /salas/<int:id_sala>/butacas` o incluir layout en alta de sala (`filas`, `asientos_por_fila`).
2. Generar butacas activas por fila/numero dentro de transacción (`ejecutar_transaccion`).
3. Repositorio: `insertar_butaca_db` / `insertar_butacas_lote_db`.
4. Validar que no se dupliquen filas/asientos.

## Fase 3 — Backend: listado admin
1. Exponer salas activas e inactivas para administración (hoy `obtener_locales_db` filtra activos).
2. Documentar endpoints en `docs/swagger.yaml`.

## Fase 4 — Frontend: backoffice
1. Crear `frontend/routes/admin_salas_routes.py` (patrón `admin_servicios`).
2. Crear `frontend/services/admin_salas_service.py`.
3. Template `frontend/templates/backoffice/salas.html` + componentes de formulario/modal.
4. CSS/JS: `admin_salas.css`, `admin_salas.js`.
5. Enlace “Gestionar salas” en `backoffice/dashboard.html`.

## Fase 5 — Datos y complejos
1. Completar seed con `entradas` para función 4 (Palermo).
2. Decidir Belgrano: agregar local/sala/butacas o quitar del footer.
3. Verificar que `obtener_estado_butacas_funcion_db` devuelva butacas para Palermo.

## Criterios de aceptación
- Admin puede crear sala y butacas desde UI.
- La compra muestra butacas para Palermo.
- No se requiere carga SQL manual para una sala nueva.
- Rama y commits siguen convenciones del proyecto.