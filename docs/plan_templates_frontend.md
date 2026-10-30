# Plan Maestro de Templates y UI - Frontend (Hito 2)
## Proyecto Integrador: Cine Paradiso (IDS 2026)

Este documento desglosa todos los templates, componentes reutilizables y la división de tareas de Frontend requerida para cumplir con la totalidad del enunciado y la Constitución Técnica ([AGENTS.md](file:///home/seba/Uba/introduccion/proyecto-final/IDS_ProyectoFinal_equipo10/AGENTS.md)).

---

## 1. Alcance y Requisitos del Enunciado (MVP Hito 2)

El Hito 2 exige la entrega de **Templates desarrollados en base a los requerimientos del cine**, sin requerir aún integración activa con la base de datos (Hito 3), pero navegables con datos simulados/maqueta y respetando la arquitectura de servidor SSR (Flask + Jinja2).

El sistema se divide en dos áreas principales:
1. **Front de Clientes (Portal Público y Usuario):**
   - Cartelera con filtros (películas clásicas/reestrenos, sinopsis, póster, duración, clasificación, funciones por local/sala).
   - Flujo de compra ágil de entradas: Selección de Función -> Matriz de Butacas (libres/ocupadas) -> Selección de Servicios Adicionales (comida, bebida, estacionamiento, VIP) -> Checkout y Confirmación con código QR y opción de cancelación.
   - Perfil de Cliente con historial de compras, consumos pasados y estado de entradas.
   - Autenticación: Login y Registro de cliente.

2. **Backoffice (Panel de Administración):**
   - Dashboard con métricas visuales: ocupación por función/película, ventas por género, franjas horarias y cancelaciones.
   - Gestión de Películas y Funciones (alta/edición de cartelera, asignación a sala/local).
   - Gestión de Servicios adicionales (alta, baja y modificación de comidas, bebidas, etc.).
   - Módulo de Control de Acceso: Validación y escaneo de códigos QR para ingreso a la sala.

---

## 2. Inventario de Templates (Páginas del Sistema)

### A. Vistas del Cliente (`frontend/templates/client/`)
| Template | Ruta sugerida | Descripción y Contenido |
| :--- | :--- | :--- |
| `cartelera.html` | `/` y `/peliculas` | Catálogo de películas con pósters, sinopsis, duración, género y botones para ver horarios. |
| `pelicula_detalle.html` | `/peliculas/<id>` | Ficha completa de la película, tráiler/información detallada y lista de funciones disponibles por local/sala. |
| `seleccion_butacas.html` | `/compra/funcion/<id>/butacas` | Mapa interactivo visual de la sala (butacas disponibles, ocupadas y seleccionadas). |
| `seleccion_servicios.html` | `/compra/servicios` | Catálogo de combos de comida, bebidas, estacionamiento y pases VIP con selector de cantidad. |
| `checkout.html` | `/compra/checkout` | Resumen del pedido (entradas + servicios), desglose de precios y formulario de confirmación. |
| `confirmacion_compra.html` | `/compra/exito/<id>` | Voucher digital con código QR de acceso a la sala, detalles de la función y botón para cancelar reserva. |
| `perfil_cliente.html` | `/perfil` | Datos del usuario, listado de compras vigentes con sus QR y pestaña de "Películas que ya vi". |
| `login.html` | `/login` | Formulario de inicio de sesión con enlaces a registro y recuperación. |
| `registro.html` | `/registro` | Formulario de registro de cliente con validaciones visuales. |

### B. Vistas del Backoffice (`frontend/templates/backoffice/`)
| Template | Ruta sugerida | Descripción y Contenido |
| :--- | :--- | :--- |
| `dashboard.html` | `/admin/dashboard` | Tarjetas de KPI y gráficos/tablas: ocupación por función, ventas por género, horarios pico y cancelaciones. |
| `peliculas_admin.html` | `/admin/peliculas` | Tabla de películas cargadas con modal/formulario para dar de alta y programar funciones en salas. |
| `servicios_admin.html` | `/admin/servicios` | Listado y ABM de servicios adicionales (comida, bebida, estacionamiento, VIP). |
| `validador_qr.html` | `/admin/validador-qr` | Pantalla de recepción para escanear/ingresar código QR y verificar validez en tiempo real. |

---

## 3. Descomposición Atómica de Componentes Reutilizables (`frontend/templates/components/`)

Para cumplir estrictamente con el principio **DRY (Don't Repeat Yourself)** y evitar duplicación de HTML, las páginas se armarán incluyendo estos componentes parametrizados:

1. **`navbar.html`**: Barra de navegación superior con logo, enlaces a Cartelera, búsqueda, estado de sesión y acceso al Backoffice si es admin.
2. **`footer.html`**: Pie de página con información de los 3 locales, legales y redes.
3. **`card_pelicula.html`**: Tarjeta con póster, badges de género/clasificación, duración y botón de acción.
4. **`mapa_butacas.html`**: Grilla que renderiza filas y columnas de asientos distinguiendo estados (libre, ocupada, seleccionada, VIP).
5. **`card_servicio.html`**: Tarjeta para ítems de confitería o extras con selector de cantidad (+ / -) y precio.
6. **`resumen_compra.html`**: Tabla/widget lateral con el subtotal dinámico de entradas y servicios seleccionados.
7. **`ticket_qr.html`**: Componente de tarjeta de embarque / voucher con código QR, fecha, sala y butacas.
8. **`kpi_card.html`**: Tarjeta de estadística para el dashboard (título, cifra principal, tendencia porcentual e icono).
9. **`alerta.html`**: Mensajes flash (éxito, error, advertencia) estilizados.
10. **`button.html`**: Botón parametrizado (`btn-primary`, `btn-secondary`, `btn-danger`, etc.).

---

## 4. Matriz de División de Tareas para el Equipo

Esta división permite que cada desarrollador del grupo tome un paquete independiente y trabaje en su propia rama `feature/<nombre>` sin pisar el trabajo de los demás:

| Paquete | Responsabilidad | Archivos Principales |
| :--- | :--- | :--- |
| **Paquete 1: Sistema de Diseño y Base** | Tokens CSS, tipografía, reset responsive, `layout.html`, `navbar.html`, `footer.html`, `alerta.html`. | `static/css/`, `templates/layout.html`, `components/navbar.html`, `components/footer.html` |
| **Paquete 2: Cartelera y Catálogo** | Vista principal de películas, filtros por fecha/local, modal de tráiler y ficha de película. | `templates/client/cartelera.html`, `pelicula_detalle.html`, `components/card_pelicula.html` |
| **Paquete 3: Selección de Butacas y Sala** | Grilla visual de sala de cine con butacas interactivas y leyenda de estados. | `templates/client/seleccion_butacas.html`, `components/mapa_butacas.html` |
| **Paquete 4: Candy Bar y Servicios Extras** | Selección de combos, comidas, bebidas, estacionamiento y pases VIP con cantidades. | `templates/client/seleccion_servicios.html`, `components/card_servicio.html` |
| **Paquete 5: Checkout y Voucher QR** | Pantalla de confirmación, desglose de compra, generación visual de QR y botón de cancelación. | `templates/client/checkout.html`, `confirmacion_compra.html`, `components/ticket_qr.html` |
| **Paquete 6: Perfil y Autenticación** | Login, registro y panel de cliente ("Mis entradas" y "Películas que ya vi"). | `templates/client/login.html`, `registro.html`, `perfil_cliente.html` |
| **Paquete 7: Dashboard de Administración** | Tarjetas KPI, gráficos y tablas de ocupación, ventas por género y cancelaciones. | `templates/backoffice/dashboard.html`, `components/kpi_card.html` |
| **Paquete 8: Gestión de Cartelera y Servicios** | Formularios y tablas para que el administrador cree películas, funciones y servicios. | `templates/backoffice/peliculas_admin.html`, `servicios_admin.html` |
| **Paquete 9: Escaneo y Validación de QR** | Pantalla de control de acceso para validar tickets y registrar ingreso a sala. | `templates/backoffice/validador_qr.html` |

---

## 5. Guía de Estilo y Tokens de Diseño Visual (Design System)

Acordado en base a los requerimientos estéticos de Cine Paradiso:
- **Atmósfera:** Modo oscuro cinematográfico tradicional con alto contraste, inspirado en salas de cine clásicas y marquesinas teatrales.
- **Tipografía:** Moderna, hiperlegible y limpia (`Outfit` o `Inter` vía Google Fonts), con jerarquía clara en titulares y etiquetas.
- **Disposición:** Visual y espaciada, priorizando pósters de alto impacto, tarjetas con profundidad y bordes redondeados sutiles, estados de butacas intuitivos y flujo de compra guiado paso a paso.

### Variables CSS Base (`frontend/static/css/style.css`):
```css
:root {
    /* Paleta Principal Cinematográfica */
    --color-bg-main: #0b1120;        /* Fondo oscuro profundo */
    --color-bg-surface: #1e293b;     /* Fondo de tarjetas y componentes */
    --color-bg-surface-hover: #334155;
    --color-border: #334155;

    /* Acentos y Señalética */
    --color-accent-red: #e11d48;     /* Rojo marquesina (botones primarios, llamadas a acción) */
    --color-accent-gold: #f59e0b;    /* Dorado cine (estrellas, VIP, destacados) */
    
    /* Tipografía y Textos */
    --font-family-base: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --color-text-main: #f8fafc;      /* Blanco tiza principal */
    --color-text-muted: #94a3b8;     /* Gris para subtítulos y metadatos */

    /* Estados de Butacas */
    --seat-available: #475569;       /* Libre (gris pizarra) */
    --seat-selected: #e11d48;        /* Seleccionada por el usuario (rojo) */
    --seat-occupied: #1e293b;        /* Ocupada (apagado / deshabilitado) */
    --seat-vip: #f59e0b;             /* Butaca VIP (dorado) */
}
```

