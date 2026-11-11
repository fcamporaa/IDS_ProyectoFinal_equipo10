import json
from datetime import datetime

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from services.funciones_service import (
    obtener_detalle_funcion_del_backend,
    obtener_funciones_del_backend,
    obtener_mapa_butacas_del_backend,
)
from services.peliculas_service import obtener_detalle_pelicula
from services.servicios_service import (
    formatear_monto,
    obtener_servicios_disponibles,
)
from utils.csrf import crear_token_csrf, validar_token_csrf
from utils.formatos import formatear_duracion, formatear_fecha_corta, formatear_hora
from validators.compras_validators import validar_servicios_seleccionados

compra_bp = Blueprint("compra", __name__, url_prefix="/compra")


def _armar_filas_butacas(butacas_lista: list[dict], butacas_seleccionadas_ids: set[int]) -> list[dict]:
    """
    Agrupa la lista plana de butacas recibida del backend por letra de fila
    y las distribuye en los tres bloques de la sala (izquierda, centro, derecha).
    """
    filas_dict = {}
    for b in butacas_lista:
        letra = b.get("fila", "A")
        if letra not in filas_dict:
            filas_dict[letra] = []

        estado_db = b.get("estado", "DISPONIBLE")
        id_butaca = b.get("id_butaca")

        if estado_db in ("OCUPADA", "RESERVADA"):
            estado = "ocupada"
        elif id_butaca in butacas_seleccionadas_ids:
            estado = "seleccionada"
        else:
            estado = "libre"

        filas_dict[letra].append({
            "id_butaca": id_butaca,
            "num": b.get("numero", 1),
            "estado": estado,
        })

    filas_ordenadas = []
    for letra in sorted(filas_dict.keys()):
        asientos = sorted(filas_dict[letra], key=lambda x: x["num"])
        total = len(asientos)

        # Distribuir proporcionalmente en 3 bloques (izq, centro, der)
        if total <= 4:
            izq = asientos[:1]
            centro = asientos[1:3]
            der = asientos[3:]
        elif total <= 6:
            izq = asientos[:1]
            centro = asientos[1:5]
            der = asientos[5:]
        elif total <= 10:
            izq = asientos[:2]
            centro = asientos[2:8]
            der = asientos[8:]
        else:
            c1 = 3
            c2 = total - 3
            izq = asientos[:c1]
            centro = asientos[c1:c2]
            der = asientos[c2:]

        filas_ordenadas.append({
            "letra": letra,
            "es_vip": letra in ("E", "F", "G"),
            "asientos_izq": izq,
            "asientos_centro": centro,
            "asientos_der": der,
        })

    return filas_ordenadas


@compra_bp.route("/butacas", methods=["GET", "POST"])
def seleccion_butacas():
    """
    Controlador SSR para el mapa de butacas en vivo.
    GET: Carga la función y el estado real de cada butaca desde el backend.
    POST: Recibe la selección del usuario, valida disponibilidad y persiste en session.
    """
    if request.method == "POST":
        id_funcion = request.form.get("id_funcion", type=int)
        raw_butacas = request.form.get("butacas_seleccionadas", "")

        ids_butacas = []
        if raw_butacas:
            try:
                ids_butacas = json.loads(raw_butacas)
            except (ValueError, TypeError):
                ids_butacas = [int(x) for x in raw_butacas.split(",") if x.strip().isdigit()]

        if not id_funcion:
            flash("No se especificó la función de cine seleccionada.", "error")
            return redirect(url_for("home.index"))

        if not ids_butacas:
            flash("Por favor seleccioná al menos una butaca libre para continuar.", "error")
            return redirect(url_for("compra.seleccion_butacas", id_funcion=id_funcion))

        # Verificar en vivo que ninguna butaca haya sido ocupada en la BD
        mapa_resp, status_mapa = obtener_mapa_butacas_del_backend(id_funcion)
        if status_mapa == 200 and isinstance(mapa_resp, dict):
            todas_butacas = mapa_resp.get("butacas", [])
            mapa_dict = {b["id_butaca"]: b for b in todas_butacas}

            butacas_elegidas = []
            for id_b in ids_butacas:
                b = mapa_dict.get(id_b)
                if not b or b.get("estado") in ("OCUPADA", "RESERVADA"):
                    flash(
                        f"La butaca elegida (Fila {b.get('fila', '')} N° {b.get('numero', '')}) ya fue reclamada o no está disponible.",
                        "error",
                    )
                    return redirect(url_for("compra.seleccion_butacas", id_funcion=id_funcion))
                butacas_elegidas.append(b)
        else:
            butacas_elegidas = [{"id_butaca": id_b, "fila": "A", "numero": id_b} for id_b in ids_butacas]

        # Obtener detalle de función para precio y datos de la orden
        func_detalle, _ = obtener_detalle_funcion_del_backend(id_funcion)
        precio_unitario = (
            float(func_detalle.get("precio_entrada", 8500))
            if isinstance(func_detalle, dict)
            else 8500.0
        )
        subtotal = precio_unitario * len(butacas_elegidas)

        # Guardar la selección en la sesión de Flask
        session["compra"] = {
            "id_funcion": id_funcion,
            "pelicula_titulo": func_detalle.get("titulo_pelicula", "Película") if isinstance(func_detalle, dict) else "Película",
            "complejo": func_detalle.get("nombre_local", "Cine Paradiso") if isinstance(func_detalle, dict) else "Cine Paradiso",
            "sala_numero": func_detalle.get("numero_sala", 1) if isinstance(func_detalle, dict) else 1,
            "sala_completa": f"Sala {func_detalle.get('numero_sala', 1)} ({func_detalle.get('formato', '2D')})" if isinstance(func_detalle, dict) else "Sala 1",
            "horario": func_detalle.get("inicio", "") if isinstance(func_detalle, dict) else "",
            "precio_unitario": precio_unitario,
            "butacas": [
                {
                    "id_butaca": b["id_butaca"],
                    "fila": b["fila"],
                    "numero": b["numero"],
                    "precio": precio_unitario,
                }
                for b in butacas_elegidas
            ],
            "total_butacas": len(butacas_elegidas),
            "subtotal_entradas": subtotal,
        }

        return redirect(url_for("compra.seleccion_servicios"))

    # Petición GET: Cargar mapa y datos
    id_funcion = request.args.get("id_funcion", type=int)
    if not id_funcion:
        id_funcion = session.get("compra", {}).get("id_funcion")

    # Si no vino id_funcion, buscar la primera función programada activa
    if not id_funcion:
        funciones_disponibles, status_f = obtener_funciones_del_backend()
        if status_f == 200 and isinstance(funciones_disponibles, list) and funciones_disponibles:
            id_funcion = funciones_disponibles[0].get("id_funcion")
        else:
            # Fallback de desarrollo / demo para permitir visualizar la vista
            id_funcion = 101

    # 1. Consultar mapa de butacas al backend
    mapa_resp, status_mapa = obtener_mapa_butacas_del_backend(id_funcion)
    # 2. Consultar detalles de la función
    func_resp, status_func = obtener_detalle_funcion_del_backend(id_funcion)

    # Obtener butacas de la sesión previa si corresponden a esta función
    compra_sesion = session.get("compra", {})
    butacas_previas = (
        compra_sesion.get("butacas", [])
        if compra_sesion.get("id_funcion") == id_funcion
        else []
    )
    ids_seleccionadas = {b["id_butaca"] for b in butacas_previas if "id_butaca" in b}

    # Armar filas dinámicas si el backend respondió
    butacas_db = mapa_resp.get("butacas", []) if isinstance(mapa_resp, dict) else []
    filas_construidas = _armar_filas_butacas(butacas_db, ids_seleccionadas)

    # Si el backend no devolvió butacas (o no está corriendo), generar sala de demostración
    if not filas_construidas:
        filas_construidas = [
            {
                "letra": letra,
                "es_vip": letra in ("E", "F", "G"),
                "asientos_izq": [
                    {"id_butaca": idx * 10 + n, "num": n, "estado": "libre"}
                    for n in range(1, 4)
                ],
                "asientos_centro": [
                    {
                        "id_butaca": idx * 10 + n,
                        "num": n,
                        "estado": "ocupada" if (letra in ("A", "D", "F") and n in (5, 6)) else "libre",
                    }
                    for n in range(4, 10)
                ],
                "asientos_der": [
                    {"id_butaca": idx * 10 + n, "num": n, "estado": "libre"}
                    for n in range(10, 13)
                ],
            }
            for idx, letra in enumerate(["A", "B", "C", "D", "E", "F", "G", "H"], start=1)
        ]

    # Buscar detalles de la película
    id_pelicula = func_resp.get("id_pelicula", 1) if isinstance(func_resp, dict) else 1
    peli_resp = obtener_detalle_pelicula(id_pelicula) if id_pelicula else None
    if not isinstance(peli_resp, dict):
        peli_resp = {}

    titulo_pelicula = (
        func_resp.get("titulo_pelicula")
        or peli_resp.get("titulo")
        or "Película en Cartelera"
    )
    poster_url = (
        peli_resp.get("poster_url")
        or "https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg"
    )
    duracion = formatear_duracion(peli_resp.get("duracion_min")) or "120 min"
    formato = func_resp.get("formato", "2D") if isinstance(func_resp, dict) else "2D"
    idioma = func_resp.get("idioma", "Original") if isinstance(func_resp, dict) else "Original"
    subtitulada = (
        "Subtitulada"
        if (func_resp.get("subtitulada") if isinstance(func_resp, dict) else True)
        else "Doblada"
    )
    complejo = (
        func_resp.get("nombre_local", "Cine Paradiso")
        if isinstance(func_resp, dict)
        else "Cine Paradiso"
    )
    num_sala = func_resp.get("numero_sala", 1) if isinstance(func_resp, dict) else 1
    precio_base = (
        float(func_resp.get("precio_entrada", 8500))
        if isinstance(func_resp, dict)
        else 8500.0
    )
    precio_vip = precio_base * 1.25

    # Formato de horario
    inicio_raw = func_resp.get("inicio", "") if isinstance(func_resp, dict) else ""
    horario_etiqueta = "Horario a confirmar"
    if inicio_raw:
        try:
            dt = datetime.fromisoformat(inicio_raw)
            horario_etiqueta = f"{formatear_fecha_corta(dt.date())} {formatear_hora(dt)}"
        except Exception:
            horario_etiqueta = inicio_raw

    # Resumen lateral
    ubicaciones_resumen = []
    subtotal = 0.0
    for b in butacas_previas:
        pr = b.get("precio", precio_base)
        subtotal += pr
        ubicaciones_resumen.append({
            "id": f"{b.get('fila')}-{b.get('numero')}",
            "id_butaca": b.get("id_butaca"),
            "fila": b.get("fila"),
            "butaca": b.get("numero"),
            "categoria": f"General {formato}",
            "precio": int(pr),
            "precio_formato": f"${int(pr):,.0f}".replace(",", "."),
        })

    datos_compra = {
        "pelicula": {
            "id_pelicula": id_pelicula,
            "titulo": titulo_pelicula,
            "titulo_upper": titulo_pelicula.upper(),
            "poster_url": poster_url,
            "formato": f"SALA {formato}",
            "idioma": f"{idioma} ({subtitulada})",
            "duracion": duracion,
        },
        "funcion": {
            "id_funcion": id_funcion,
            "complejo": complejo,
            "sala_nombre": f"Sala {num_sala}",
            "sala_completa": f"Sala {num_sala} ({formato})",
            "horario_etiqueta": horario_etiqueta,
            "pantalla_tipo": f"PANTALLA {formato}",
            "tiempo_restante": "10:00 min",
            "precio_general": int(precio_base),
            "precio_vip": int(precio_vip),
        },
        "sala": {
            "filas": filas_construidas,
        },
        "resumen": {
            "total_butacas": len(ubicaciones_resumen),
            "ubicaciones": ubicaciones_resumen,
            "subtotal": int(subtotal),
            "subtotal_formato": f"${int(subtotal):,.0f}".replace(",", "."),
            "cargo_servicio": 0,
            "cargo_servicio_texto": "Bonificado $0",
            "total": int(subtotal),
            "total_formato": f"${int(subtotal):,.0f}".replace(",", "."),
        },
    }

    return render_template("seleccion_butacas.html", c=datos_compra)


@compra_bp.route("/servicios", methods=["GET", "POST"])
def seleccion_servicios():
    """Renderiza Candy Bar y conserva sus cantidades en la sesión Flask."""
    if request.method == "POST":
        if not validar_token_csrf(request.form.get("csrf_token", "")):
            flash("Formulario vencido o CSRF inválido.", "error")
            return redirect(url_for("compra.seleccion_servicios"))

        if request.form.get("accion") == "omitir":
            session["servicios_seleccionados"] = []
            return redirect(url_for("compras.checkout"))

        try:
            servicios = validar_servicios_seleccionados(
                request.form.get("servicios_json", "[]")
            )
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("compra.seleccion_servicios"))

        catalogo = obtener_servicios_disponibles()
        if catalogo is None:
            flash("No se pudo validar el catálogo de servicios.", "error")
            return redirect(url_for("compra.seleccion_servicios"))
        ids_disponibles = {servicio["id_servicio"] for servicio in catalogo}
        if any(item["id_servicio"] not in ids_disponibles for item in servicios):
            flash(
                "La selección contiene un servicio que ya no está disponible.",
                "error",
            )
            return redirect(url_for("compra.seleccion_servicios"))

        session["servicios_seleccionados"] = servicios
        return redirect(url_for("compras.checkout"))

    servicios_api = obtener_servicios_disponibles()
    if servicios_api is None:
        flash("No se pudo cargar el catálogo de servicios.", "error")
        servicios_api = []

    cantidades = {
        item["id_servicio"]: item["cantidad"]
        for item in session.get("servicios_seleccionados", [])
    }
    servicios = [
        {**servicio, "cantidad": cantidades.get(servicio["id_servicio"], 0)}
        for servicio in servicios_api
    ]
    subtotal_entradas = 17000
    items_seleccionados = [
        {
            "id_servicio": servicio["id_servicio"],
            "nombre": servicio["nombre"],
            "descripcion": servicio["descripcion"],
            "cantidad": servicio["cantidad"],
            "subtotal_formato": formatear_monto(
                servicio["precio"] * servicio["cantidad"]
            ),
        }
        for servicio in servicios
        if servicio["cantidad"] > 0
    ]
    subtotal_candy = sum(
        servicio["precio"] * servicio["cantidad"]
        for servicio in servicios
    )

    datos_compra = {
        "pelicula": {
            "id_pelicula": 2,
            "titulo": "Furiosa: Saga Mad Max",
            "titulo_upper": "FURIOSA: SAGA MAD MAX",
            "poster_url": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=300&auto=format&fit=crop&q=80",
            "formato": "SALA 2 • 4D",
            "sala_badge": "SALA 2 • 4D",
            "idioma": "Subtitulada",
            "horario_etiqueta": "Hoy 20:15 hs • Subtitulada",
            "complejo": "Paradiso Centro (Corrientes 1240)",
        },
        "entradas": {
            "items": [
                {
                    "descripcion": "2x Entrada General 4D",
                    "detalle": "Butacas E-08, E-09",
                    "subtotal": subtotal_entradas,
                    "subtotal_formato": formatear_monto(subtotal_entradas),
                }
            ],
            "subtotal": subtotal_entradas,
            "subtotal_formato": formatear_monto(subtotal_entradas),
        },
        "categorias_filtro": [
            {"id": "todos", "nombre": "Todos los Servicios"},
            {"id": "comida", "nombre": "COMIDA"},
            {"id": "bebida", "nombre": "BEBIDA"},
        ],
        "servicios": servicios,
        "servicios_seleccionados": [
            item for item in session.get("servicios_seleccionados", [])
        ],
        "candy_seleccionado": {
            "items": items_seleccionados,
            "total_items": sum(item["cantidad"] for item in items_seleccionados),
            "subtotal": subtotal_candy,
            "subtotal_formato": formatear_monto(subtotal_candy),
        },
        "resumen": {
            "subtotal_entradas": subtotal_entradas,
            "subtotal_entradas_formato": formatear_monto(subtotal_entradas),
            "subtotal_candy": subtotal_candy,
            "subtotal_candy_formato": formatear_monto(subtotal_candy),
            "cargos_servicio_texto": "100% Bonificado",
            "total": subtotal_entradas + subtotal_candy,
            "total_formato": formatear_monto(subtotal_entradas + subtotal_candy),
        },
    }

    return render_template(
        "seleccion_servicios.html",
        c=datos_compra,
        csrf_token=crear_token_csrf(),
    )


@compra_bp.route("/checkout")
def seleccion_checkout():
    """
    Renderiza la pantalla de Checkout y Pago final de la reserva.
    Presenta los datos del comprador, formulario de tarjeta con cuotas y el resumen consolidado.
    """
    datos_compra = {
        "tiempo_restante": "08:40",
        "pelicula": {
            "id_pelicula": 1,
            "titulo": "Dune: Parte Dos",
            "poster_url": "https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg",
            "badge_formato": "4D MOTION",
            "badge_edad": "+13",
            "especificaciones": "Subtitulada • 166 min",
            "sala_completa": "Sala 1 (Atmos 4D Extreme)",
            "dia_horario": "Viernes 24/10/2026 • 19:30 hs",
            "complejo": "Cine Paradiso Centro",
            "butacas_asignadas": "Fila E • Butacas 7, 8 (VIP 4D)",
        },
        "desglose": [
            {
                "titulo": "2x Entrada 4D Subtitulada ($8.500 c/u)",
                "subtexto": None,
                "precio": "$17.000",
            },
            {
                "titulo": "1x Combo Mega Paradiso",
                "subtexto": "1 Balde Popcorn XL + 2 Gaseosas 750ml + 1 Golosina",
                "precio": "$14.500",
            },
            {
                "titulo": "Estacionamiento Prepago (4 hs)",
                "subtexto": "Acceso por calle Cerrito 1150",
                "precio": "$4.500",
            },
        ],
        "subtotal_parcial": "$36.000",
        "cargo_servicio": "BONIFICADO ($0)",
        "total": "$36.000",
        "total_monto": 36000,
        "cuotas": [
            "3 cuotas de $12.000 (Programa Cuota Simple - Sin Interés)",
            "1 pago de $36.000 (Sin Interés)",
            "6 cuotas fijas de $7.200",
        ],
        "comprador_default": {
            "nombre": "Mateo Alessandro Rossi",
            "email": "mateo.rossi@cinemaparadiso.com.ar",
            "dni": "39.842.109",
            "telefono": "+54 9 11 4982-3390",
            "tarjeta_numero": "4509 •••• •••• 8821",
            "tarjeta_titular": "MATEO A ROSSI",
            "tarjeta_vencimiento": "08/29",
        },
    }

    return render_template("checkout.html", c=datos_compra)


@compra_bp.route("/confirmacion")
@compra_bp.route("/confirmacion/<int:id_compra>")
def confirmacion_compra(id_compra: int = 89421):
    """
    Renderiza la pantalla de Confirmación de Compra y Comprobante Oficial (Paso 4).
    Muestra el voucher digital de acceso a sala con código QR, detalle de facturación AFIP,
    política de cancelación autogestionable e instrucciones de sala.
    """
    datos_confirmacion = {
        "id_transaccion": "#CP-2026-89421",
        "email_comprador": "mateo.rossi@cinemaparadiso.com.ar",
        "codigo_qr": "QR-CP-89421-E7E8",
        "pelicula": {
            "id_pelicula": 1,
            "titulo": "Dune: Parte Dos",
            "poster_url": "https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg",
            "badge_poster": "4D ATMOS",
            "clasificacion": "SAM 13",
            "duracion": "166 MIN",
            "formato_sala": "4D D-BOX",
            "idioma": "SUBTITULADA",
            "direccion_sonido": "Dirección: Denis Villeneuve • Formato de Sonido Dolby Atmos 64 Canales",
            "fecha": "Vie 24 Oct 2026",
            "horario": "19:30 hs",
            "complejo": "Centro (Corrientes 1240)",
            "sala_nombre": "AUDITORIO CENTRO • SALA 1",
            "butacas": "Fila E • Asientos 7 y 8",
            "badge_butacas": "VIP D-BOX 4D",
        },
        "facturacion": {
            "tipo": "FACTURA B • AFIP",
            "items": [
                {"descripcion": "2x Entrada 4D Subtitulada (Fila E: 7, 8)", "monto": "$17.000"},
                {"descripcion": "1x Combo Mega Paradiso (Candy Bar)", "monto": "$14.500"},
                {"descripcion": "1x Estacionamiento Prepago (4 hs)", "monto": "$4.500"},
            ],
            "cargo_servicio": "100% BONIFICADO",
            "cargo_servicio_monto": "$0",
            "total": "$36.000",
            "iva_discriminado": "$6.247,93",
            "tarjeta_info": "Mastercard finalizada en 8821",
            "cuotas_info": "Aprobado en 3 cuotas fijas de $12.000",
            "cae": "CAE Nº: 74920194820184",
            "vto_cae": "Fecha Vto CAE: 03/11/2026",
        },
        "adicionales": [
            {
                "tipo": "combo",
                "nombre": "1x Combo Mega Paradiso",
                "detalle": "Balde Pochoclos + 2 Bebidas Grandes",
                "estado": "Listo",
                "icono": "combo",
            },
            {
                "tipo": "cochera",
                "nombre": "1x Cochera Prepaga",
                "detalle": "Hasta 4 hs cubiertas (Corrientes 1240)",
                "subdetalle": "PATENTE: AB-829-QX",
                "estado": "Activo",
                "icono": "parking",
            },
        ],
        "cancelacion": {
            "limite_texto": "Viernes 24/10 hasta las 17:30 hs",
        },
    }

    return render_template("confirmacion_compra.html", c=datos_confirmacion)
