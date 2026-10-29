---
name: 04-revisar-y-commitear
description: Úsala al finalizar el desarrollo de una tarea cuando el usuario quiera revisar la calidad del código, validar su uniformidad, hacer commit o subir los cambios a su rama en GitHub.
---

# Target
Ejecutar una auditoría integral de modularidad, reutilización y cumplimiento de estándares sobre los archivos modificados, validar que el desarrollador comprenda el código para su evaluación oral y generar el commit hacia la rama de trabajo.

# Inputs
1. Estado actual del repositorio y diferencias de código (`git status` y `git diff`).
2. Reglas de arquitectura y restricciones definidas en `AGENTS.md`.

# Procedure
1. **Auditoría de Modularidad, Reutilización y Uniformidad:** Analiza el `git diff` completo y verifica:
   - **Backend:** ¿Se escribió alguna validación, constante o función auxiliar dentro de una ruta/servicio que ya existía o que debería extraerse a `backend/src/utils.py` o `backend/src/constants.py`? ¿Las 4 capas mantienen exactamente el mismo estilo y estructura de retorno que el resto del proyecto? ¿Se actualizó `backend/docs/swagger.yaml`?
   - **Frontend:** ¿Se escribió HTML repetitivo (botones, cards, alertas, inputs) fijo dentro de una vista en lugar de extraerlo o invocarlo como componente parametrizado en `frontend/templates/components/`? ¿Todas las rutas y recursos usan `url_for()` y extienden de la plantilla base?
   - *Acción correctiva:* Si detectas cualquier oportunidad de mejora en la modularización o uniformidad, refactorízala y muéstrasela al usuario antes de avanzar al siguiente paso.
2. **Verificación de Invariantes Técnicos:**
   - Confirma ausencia total de clases (`class`), ORMs, llamadas `fetch()`/`axios` al backend, campos de fecha/hora separados, variables globales o comentarios línea por línea.
   - Confirma que archivos sensibles o de entorno local (`.env`, `venv/`, `.venv/`, `__pycache__/`) no estén en el área de staging.
3. **Validación de Comprensión para Evaluación Oral:**
   - Formula 2 preguntas técnicas puntuales al desarrollador sobre los cambios realizados (por ejemplo: cómo fluyen los datos entre las capas modificadas, cómo funciona el pasaje de variables al componente Jinja2 o qué código HTTP retorna ante un fallo).
   - Espera su respuesta y aclara cualquier concepto necesario hasta que el desarrollador domine por completo su entrega.
4. **Generación de Commit y Cierre de Flujo en Equipo:**
   - Propón los comandos exactos para agregar únicamente los archivos de la tarea (`git add ...`) y realizar el commit con el formato declarativo del equipo:
     `git commit -m "[MODULO] Descripción concisa del cambio realizado (#TareaID)"`
   - Indica el comando para subir la rama actual (`git push origin <nombre-rama>`) y recuérdale abrir el Pull Request hacia `develop` avisando a sus compañeros para la revisión cruzada antes de hacer merge.

# Constraints
- Prohibido hacer commit o push directo sobre las ramas `main` o `develop`.
- Prohibido dar por cerrada la revisión sin haber comprobado que no exista código duplicado en `utils.py` o `templates/components/`.

# Outputs
Reporte de auditoría de modularidad (`PASS` o refactorizaciones aplicadas), las 2 preguntas de validación oral y el bloque de comandos Git listos para ejecutar.
