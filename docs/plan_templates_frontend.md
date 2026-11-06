# Plan Maestro de Templates y UI - Frontend (Hito 2)
## Proyecto Integrador: Cine Paradiso (IDS 2026)
### Estética: Cinematic Precision (Dark Theme Profesional)

Este documento desglosa todos los templates, componentes reutilizables y la división de tareas de Frontend requerida para cumplir con la totalidad del enunciado, la Constitución Técnica ([AGENTS.md](file:///home/seba/Uba/introduccion/proyecto-final/IDS_ProyectoFinal_equipo10/AGENTS.md)) y el contrato OpenAPI ([docs/swagger.yaml](file:///home/seba/Uba/introduccion/proyecto-final/IDS_ProyectoFinal_equipo10/docs/swagger.yaml)).

---

## 1. Alcance y Requisitos del Enunciado (MVP Hito 2)

El Hito 2 exige la entrega de **Templates desarrollados y navegables en base a los requerimientos del cine**, sin requerir aún integración activa con la base de datos (Hito 3), pero maquetados con datos simulados y respetando la arquitectura de servidor SSR (Flask + Jinja2).

### Reglas Estrictas de Dominio (Sin Datos Fantasiosos):
- **Formatos de Sala:** Únicamente `2D`, `3D` y `4D` (según `funciones.formato` en la BD).
- **Los 3 Complejos Reales:**
  1. *Cine Paradiso Centro:* Av. Corrientes 1240, CABA
  2. *Cine Paradiso Palermo:* Humboldt 1920 (Palermo Soho), CABA
  3. *Cine Paradiso Belgrano:* Av. Cabildo 2180, CABA
- **Películas Reestrenos:** Título, sinopsis, póster 2:3, trailer URL, duración, clasificación (`ATP`, `+13`, `+16`, `+18`), año de estreno (`anio_estreno`) y géneros.
- **Funciones:** Cada horario representa un `id_funcion` con hora (`inicio`), sala (`Sala 1`) y formato (`2D`/`3D`/`4D`).

---

## 2. Inventario de Templates (Páginas del Sistema)

### A. Vistas del Cliente (`frontend/templates/client/`)
| Template | Ruta sugerida | Descripción y Contenido |
| :--- | :--- | :--- |
| `cartelera.html` | `/` y `/peliculas` | Catálogo de películas con pósters 2:3, formatos reales (2D/3D/4D), clasificación y botones de horarios por sala. |
| `pelicula_detalle.html` | `/peliculas/<id>` | Ficha completa de la película, tráiler y lista de funciones disponibles por complejo. |
| `seleccion_butacas.html` | `/compra/funcion/<id>/butacas` | Mapa interactivo de la sala (butacas libres `#242830`, seleccionadas `#f59e0b` y ocupadas `#1b1b1f`). |
| `seleccion_servicios.html` | `/compra/servicios` | Catálogo de combos de candy bar, comidas, bebidas y extras con selector de cantidad. |
| `checkout.html` | `/compra/checkout` | Resumen del pedido (entradas + servicios), desglose de precios y formulario de confirmación. |
| `confirmacion_compra.html` | `/compra/exito/<id>` | Voucher digital con código QR de acceso a la sala, detalles de función y botón para cancelar reserva. |
| `perfil_cliente.html` | `/perfil` | Datos del usuario, listado de compras con sus QR y pestaña de "Películas que ya vi". |
| `login.html` | `/login` | Formulario de inicio de sesión con enlaces a registro. |
| `registro.html` | `/registro` | Formulario de registro de cliente. |

### B. Vistas del Backoffice (`frontend/templates/backoffice/`)
| Template | Ruta sugerida | Descripción y Contenido |
| :--- | :--- | :--- |
| `dashboard.html` | `/admin/dashboard` | KPIs de ocupación por función/película, ventas por género, horarios pico y cancelaciones. |
| `peliculas_admin.html` | `/admin/peliculas` | Tabla de películas cargadas con formulario para dar de alta y programar funciones en salas. |
| `servicios_admin.html` | `/admin/servicios` | Listado y ABM de servicios adicionales (comida, bebida, combos). |
| `validador_qr.html` | `/admin/validador-qr` | Pantalla de recepción para escanear/ingresar código QR y registrar ingreso a sala. |

---

## 3. Descomposición Atómica de Componentes Reutilizables (`frontend/templates/components/`)

1. **`navbar.html`**: Header sticky oscuro con isotipo de claqueta SVG, selector de complejo (Centro, Palermo, Belgrano), buscador compacto y acceso a login.
2. **`footer.html`**: Pie institucional de 4 columnas (Identidad, Navegación, 3 Complejos con direcciones reales y Legal).
3. **`barra_filtros.html`**: Píldoras de fecha ("Hoy", "Mañana", "Mié"), chips de géneros reales y leyenda de disponibilidad.
4. **`hero_destacado.html`**: Banner panorámico de la película destacada con gradiente envolvente, badges y horarios directos.
5. **`card_pelicula.html`**: Tarjeta 2:3 con póster, badges de formato (2D/3D/4D), clasificación, duración, horarios interactivos y botón "Seleccionar Butacas".
6. **`mapa_butacas.html`**: Grilla de asientos (disponible, seleccionada, ocupada, VIP).
7. **`card_servicio.html`**: Tarjeta de confitería con selector de cantidad (+ / -) y precio unitario.
8. **`resumen_compra.html`**: Widget lateral con el subtotal dinámico de entradas y servicios.
9. **`ticket_qr.html`**: Voucher con código QR, código de reserva, sala y butacas.
10. **`button.html`**: Botón parametrizado (`btn-primary`, `btn-secondary`, `btn-gold`, `btn-outline`, `btn-danger`).
11. **`alerta.html`**: Notificaciones visuales (`info`, `success`, `warning`, `danger`).

---

## 4. Guía de Tokens de Diseño (`frontend/static/css/tokens.css`)

```css
:root {
    --color-bg-main: #121316;              /* Fondo oscuro base */
    --color-bg-surface-low: #1b1b1f;       /* Paneles y barras secundarias */
    --color-bg-surface: #1f1f23;           /* Tarjetas y contenedores */
    --color-bg-surface-high: #292a2d;      /* Elementos elevados y hover */
    --color-bg-surface-highest: #343538;   /* Bordes activos */
    --color-border: #26272b;               /* Bordes nítidos de 1px */
    
    --color-accent-red: #e50914;           /* Rojo Cinema Paradiso (CTAs) */
    --color-accent-gold: #f59e0b;          /* Dorado ámbar (VIP, destacados) */
    
    --font-family-base: 'Inter', sans-serif;
    --color-text-main: #f3f4f6;
    --color-text-muted: #9ca3af;
    
    --radius-sm: 4px;
    --radius-md: 6px;
    --radius-lg: 8px;
    --radius-full: 9999px;
}
```
