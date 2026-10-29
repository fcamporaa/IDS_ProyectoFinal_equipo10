---
name: 01-planificar-y-reutilizar
description: Úsala OBLIGATORIAMENTE al iniciar cualquier tarea, funcionalidad, vista o corrección antes de escribir código. Analiza el requerimiento, audita el código existente para reutilizar funciones o componentes UI, y genera el plan de implementación. NO la uses cuando ya exista un plan aprobado en la conversación actual.
---

# Target
Transformar el requerimiento de la tarea en una especificación clara (Spec) y un plan técnico modular (Plan) que maximice la reutilización de activos existentes en `backend/src/` y `frontend/`, garantizando uniformidad en todo el proyecto.

# Inputs
1. Descripción de la tarea asignada al desarrollador en el tablero del proyecto (título, objetivos y número de issue/tarea).
2. Archivos transversales del repositorio según el área afectada:
   - Backend: `backend/src/constants.py`, `backend/src/utils.py`, `backend/src/exceptions.py`, `backend/db/init_db.sql`.
   - Frontend: `frontend/utils/`, `frontend/templates/layout.html` (o `base.html`), `frontend/templates/components/`, `frontend/static/css/`.

# Procedure
1. **Verificación de Rama de Trabajo:** Confirma con el usuario el número/nombre de su tarea y recuérdale trabajar sobre una rama específica creada desde `develop` (`feature/<modulo>` o `fix/<descripcion>`), nunca sobre `main`.
2. **Auditoría de Reutilización y Patrones Existentes:**
   - Inspecciona los archivos transversales listados en `# Inputs` y al menos un módulo vecino ya implementado.
   - Identifica qué funciones de `utils.py`, constantes de `constants.py`, decoradores de `frontend/utils/` o componentes HTML de `templates/components/` resuelven total o parcialmente partes de esta tarea.
   - Si la tarea requiere elementos repetibles que aún no existen (ej. una validación de formato en backend, o una tarjeta `card.html`, un botón `button.html` o un campo de formulario en frontend), planifica su creación como **módulo/componente genérico reutilizable** antes de construir la ruta o vista específica.
3. **Clarificación de Especificación (Spec):** Si existen ambigüedades en entradas, salidas, validaciones o permisos, formula un máximo de 3 preguntas concretas al usuario.
4. **Formulación del Plan de Implementación:** Presenta una propuesta estructurada detallando:
   - **Activos a reutilizar:** Funciones, constantes y componentes existentes que se importarán o incluirán.
   - **Nuevos activos reutilizables a crear:** Utilidades en `utils.py` o componentes parametrizados en `templates/components/`.
   - **Archivos específicos a modificar/crear:** Secuencia paso a paso por capa.
5. **Punto de Control Humano:** Detén la ejecución y solicita confirmación explícita del usuario sobre el plan antes de generar código de implementación.

# Outputs
Reporte estructurado en Markdown con las secciones: `1. Rama sugerida`, `2. Auditoría de Reutilización`, `3. Plan Paso a Paso por Archivo` y pregunta de confirmación.
