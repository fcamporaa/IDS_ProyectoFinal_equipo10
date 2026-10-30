<!-- Regla de Workspace para Antigravity -->
<!-- Este archivo sincroniza e importa las directivas de la Constitución Técnica -->

Este proyecto se rige de manera obligatoria e inmutable por la Constitución Técnica definida en:
[AGENTS.md](file:///home/seba/Uba/introduccion/proyecto-final/IDS_ProyectoFinal_equipo10/AGENTS.md)

### Resumen de Cumplimiento Obligatorio:
1. **Paradigma procedural**: Prohibido usar clases (`class`) para modelos, controladores o servicios. Prohibido usar ORMs. SQL explícito con `%s`.
2. **Arquitectura SSR**: Prohibido el uso de `fetch()`, `axios` o AJAX en JavaScript. Toda comunicación navegador-servidor es vía HTML (`GET`/`POST`). Frontend consume backend en Python mediante `requests`.
3. **Estructura Backend en 4 Capas**: `routes` -> `validators` -> `services` -> `repositories`.
4. **Fechas y Horas**: Almacenamiento unificado en campos `DATETIME`.
5. **Protocolo de Skills**:
   - `01-planificar-y-reutilizar` antes de escribir código.
   - `02-desarrollar-backend` y `03-desarrollar-frontend` solo con plan aprobado.
   - `04-revisar-y-commitear` antes de cualquier commit.

Consulta siempre el archivo maestro [AGENTS.md](file:///home/seba/Uba/introduccion/proyecto-final/IDS_ProyectoFinal_equipo10/AGENTS.md) para detalles completos de arquitectura y restricciones.
