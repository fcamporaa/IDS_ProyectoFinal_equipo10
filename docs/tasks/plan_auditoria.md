# Plan de acción — Auditoría técnica

## Objetivo
Transformar los hallazgos de la auditoría en acciones priorizadas para corregir errores reales y mejorar mantenibilidad, sin modificar el proyecto durante la auditoría.

## Hallazgos priorizados

### Prioridad Alta
1. **Completar datos de Palermo**
   - Agregar `entradas` para función 4 en `backend/db/seed_data.sql`.
   - Verificar en BD real que la función esté vigente.
2. **Decidir Belgrano**
   - Agregar local/sala/butacas en seed o quitar del footer (`frontend/templates/components/footer.html`).
3. **Pago simulado en desarrollo**
   - Documentar `ALLOW_SIMULATED_PAYMENTS=true` en `.env.example`.
   - Confirmar que `procesar_compra` complete el flujo.

### Prioridad Media
4. **Implementar backoffice de salas** (ver `plan_backoffice_salas_butacas.md`).
5. **Revisar error handler global** (`backend/app.py`) para no ocultar errores de programación.
6. **Validar configuración de JWT** (`JWT_SECRET_KEY` no nulo) en `.env.example` y arranque.

### Prioridad Baja
7. **Agregar tests básicos** para compra y salas.
8. **Refactor menor** de redundancia de roles en `constants.py`.
9. **Revisar tamaño de `compra_routes.py`** (opcional, extraer helpers).

## Plan de verificación
- Ejecutar backend + BD y probar mapa de butacas de Palermo.
- Probar flujo completo de compra con pago simulado habilitado.
- Revisar que no haya complejos inexistentes en UI.

## Notas
- La auditoría fue solo lectura; este archivo define el plan de implementación posterior.
- No se modificaron archivos durante la auditoría.