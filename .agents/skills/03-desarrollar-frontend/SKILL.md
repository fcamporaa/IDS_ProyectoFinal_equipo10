---
name: 03-desarrollar-frontend
description: Úsala para crear o modificar vistas Jinja2, componentes UI reutilizables, hojas de estilo CSS, rutas web o servicios HTTP con `requests` dentro de `frontend/` tras aprobar el plan. NO la uses para endpoints de la API Backend ni consultas SQL.
---

# Target
Desarrollar vistas y pantallas en `/frontend` bajo una arquitectura de diseño atómico y modular en Jinja2, donde cada elemento visual repetible (botones, cards, alertas, inputs, modales, tablas) se construye como un componente parametrizado en `frontend/templates/components/` y se reutiliza en todas las páginas pasándole datos dinámicos.

# Inputs
1. Plan de implementación aprobado en la sesión actual.
2. Plantilla maestra `frontend/templates/layout.html` (o `base.html`), carpeta `frontend/templates/components/`, hojas de estilo en `frontend/static/css/`, `frontend/utils/` y `frontend/services/`.

# Procedure
1. **Diseño Modular de Componentes UI (`frontend/templates/components/`):**
   - **Prohibido escribir HTML repetitivo directamente en las páginas.** Antes de armar una vista en `client/` o `backoffice/`, descompón la interfaz en piezas reutilizables (ej. `button.html`, `card_pelicula.html`, `modal.html`, `alert.html`, `form_input.html`).
   - Diseña cada archivo en `templates/components/` como una plantilla parametrizada que recibe variables de Jinja (por ejemplo: `{{ texto }}`, `{{ url_destino }}`, `{{ variante_clase | default('btn-primary') }}`, `{{ tipo | default('button') }}`, `{{ item.titulo }}`) y aplica clases CSS unificadas definidas en `frontend/static/css/`.
   - De este modo, cuando cualquier vista necesite renderizar 1, 3 o 10 botones o tarjetas con el mismo diseño, simplemente invoca el componente rellenando sus datos con:
     `{% with texto='Confirmar', url_destino=url_for('compras.confirmar'), variante_clase='btn-primary' %}{% include 'components/button.html' %}{% endwith %}`
     o dentro de un bucle `{% for pelicula in peliculas %}{% include 'components/card_pelicula.html' %}{% endfor %}`.
2. **Estructura de la Vista (`frontend/templates/client/` o `backoffice/`):**
   - Inicia siempre extendiendo la plantilla base (`{% extends 'layout.html' %}` o `base.html`) e inyecta el contenido en los bloques correspondientes (`{% block content %}`).
   - Ensambla la página combinando los componentes de `templates/components/`.
   - Utiliza obligatoriamente `{{ url_for('nombre_blueprint.nombre_funcion', ...) }}` para todo atributo `href` o `action`, y `{{ url_for('static', filename='...') }}` para archivos CSS, imágenes y JS visual.
3. **Capa de Comunicación (`frontend/services/`) y Utilidades (`frontend/utils/`):**
   - Reutiliza o agrega en `frontend/services/` las funciones que realizan peticiones HTTP (`requests.get`, `requests.post`, etc.) hacia la API del Backend respetando el manejo de errores existente.
   - En rutas que requieran autenticación o rol de administrador, importa y aplica los decoradores existentes en `frontend/utils/` (`@login_required`, `@role_required`).
4. **Controlador Web (`frontend/routes/`):**
   - En peticiones `GET`, obtén los datos desde `frontend/services/` y pásalos como diccionario de contexto a `render_template(...)`.
   - En peticiones `POST`, captura `request.form`, envíalo a través de `frontend/services/`, notifica el resultado con `flash()` y redirige mediante `redirect(url_for(...))`.
5. **Transferencia de Conocimiento:** Explica al usuario qué parámetros recibe cada componente creado o reutilizado y cómo viajan los datos desde la ruta de Flask hasta el componente Jinja2.

# Constraints
- Prohibido usar `fetch()`, `axios` o AJAX en el navegador para consumir el Backend.
- Prohibido hardcodear rutas URL o rutas a archivos estáticos sin `url_for()`.
- Prohibido duplicar estructuras HTML de botones, tarjetas o barras de navegación en múltiples vistas en lugar de parametrizarlas en `templates/components/`.

# Outputs
Archivos de componentes en `templates/components/`, estilos en `static/css/`, vistas ensambladas, rutas/servicios en `frontend/` y guía breve de los parámetros que acepta cada componente.
