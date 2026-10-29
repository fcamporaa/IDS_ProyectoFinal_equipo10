---
name: 02-desarrollar-backend
description: Úsala para implementar o modificar código dentro de `backend/src/` (routes, validators, services, repositories, utils, constants), `backend/db/init_db.sql` o `backend/docs/swagger.yaml` una vez que el plan haya sido aprobado. NO la uses para vistas HTML ni sin un plan aprobado.
---

# Target
Implementar lógica de Backend en Flask y MySQL respetando las 4 capas del proyecto, manteniendo consistencia estilística absoluta con los módulos existentes y centralizando toda lógica común en `src/utils.py` y `src/constants.py`.

# Inputs
1. Plan de implementación aprobado en la sesión actual.
2. Archivos del módulo objetivo en `backend/src/` y archivos compartidos (`constants.py`, `utils.py`, `exceptions.py`, `db.py`, `docs/swagger.yaml`).

# Procedure
1. **Alineación de Estilo y Contratos:** Lee un módulo ya existente en `backend/src/` para replicar exactamente la misma estructura de imports, nombres de variables, manejo de diccionarios de retorno y captura de errores.
2. **Extracción a Capa Transversal (`constants.py` y `utils.py`):**
   - Si necesitas códigos HTTP, estados o valores fijos, impórtalos o agrégalos en `backend/src/constants.py`.
   - Si necesitas validar tipos de datos, fechas `DATETIME`, correos, rangos numéricos, formatear respuestas JSON o enviar correos, utiliza las funciones de `backend/src/utils.py`. Si una función genérica no existe aún, créala en `backend/src/utils.py` con parámetros claros para que cualquier otro módulo del equipo pueda invocarla.
3. **Desarrollo Secuencial en las 4 Capas:**
   - `src/repositories/<modulo>_repository.py`: Escribe funciones de acceso a datos con queries SQL puras y parametrizadas (`%s`) usando `src/db.py`. Retorna diccionarios o listas de diccionarios.
   - `src/validators/<modulo>_validators.py`: Escribe funciones que validen los datos de entrada invocando a las utilidades de `src/utils.py`.
   - `src/services/<modulo>_services.py`: Implementa las reglas de negocio orquestando llamadas a `validators` y `repositories`.
   - `src/routes/<modulo>_routes.py`: Registra el endpoint en el Blueprint, extrae datos de `request`, invoca al servicio y retorna `jsonify(...)` junto al código HTTP de `constants.py`.
4. **Sincronización de Documentación:** Actualiza `backend/docs/swagger.yaml` reflejando la ruta, parámetros de entrada, estructura JSON de respuesta y códigos de estado del endpoint.
5. **Transferencia de Conocimiento:** Explica brevemente el flujo de datos implementado a través de las 4 capas para asegurar que el desarrollador pueda explicarlo con solvencia en su evaluación técnica oral.

# Constraints
- Prohibido usar `class` (POO) o librerías ORM.
- Prohibido escribir consultas SQL fuera de `src/repositories/`.
- Prohibido duplicar validaciones o formateos que ya existan en `src/utils.py`.

# Outputs
Código implementado por capa, actualización de `swagger.yaml` y resumen técnico de trazabilidad (funciones reutilizadas y flujo de ejecución).
