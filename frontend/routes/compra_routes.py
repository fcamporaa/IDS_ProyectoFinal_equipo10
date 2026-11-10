from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from services.servicios_service import (
    formatear_monto,
    obtener_servicios_disponibles,
)
from utils.csrf import crear_token_csrf, validar_token_csrf
from validators.compras_validators import validar_servicios_seleccionados

compra_bp = Blueprint("compra", __name__, url_prefix="/compra")


@compra_bp.route("/butacas")
def seleccion_butacas():
    """
    Renderiza la pantalla de selección de butacas de una función.
    Provee el contexto estructurado de sala, filas y resumen para este hito visual SSR.
    """
    datos_compra = {
        "pelicula": {
            "id_pelicula": 1,
            "titulo": "Dune: Parte Dos",
            "titulo_upper": "DUNE: PARTE DOS",
            "poster_url": "https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg",
            "formato": "SALA 4D",
            "idioma": "Subtitulada",
            "duracion": "166 min",
        },
        "funcion": {
            "id_funcion": 102,
            "complejo": "Cine Paradiso Centro",
            "sala_nombre": "Sala 1",
            "sala_completa": "Sala 1 (4D Atmos)",
            "horario_etiqueta": "Hoy 19:30 hs",
            "pantalla_tipo": "PANTALLA CURVA MAXVISION 4D",
            "tiempo_restante": "08:40 min",
            "precio_general": 8500,
            "precio_vip": 10500,
        },
        "sala": {
            "filas": [
                {
                    "letra": "A",
                    "es_vip": False,
                    "asientos_izq": [{"num": 1, "estado": "libre"}, {"num": 2, "estado": "libre"}, {"num": 3, "estado": "libre"}],
                    "asientos_centro": [
                        {"num": 4, "estado": "libre"}, {"num": 5, "estado": "ocupada"},
                        {"num": 6, "estado": "ocupada"}, {"num": 7, "estado": "libre"},
                        {"num": 8, "estado": "libre"}, {"num": 9, "estado": "libre"}
                    ],
                    "asientos_der": [{"num": 10, "estado": "libre"}, {"num": 11, "estado": "libre"}, {"num": 12, "estado": "libre"}]
                },
                {
                    "letra": "B",
                    "es_vip": False,
                    "asientos_izq": [{"num": 1, "estado": "libre"}, {"num": 2, "estado": "libre"}, {"num": 3, "estado": "libre"}],
                    "asientos_centro": [
                        {"num": 4, "estado": "ocupada"}, {"num": 5, "estado": "ocupada"},
                        {"num": 6, "estado": "libre"}, {"num": 7, "estado": "libre"},
                        {"num": 8, "estado": "libre"}, {"num": 9, "estado": "libre"}
                    ],
                    "asientos_der": [{"num": 10, "estado": "libre"}, {"num": 11, "estado": "libre"}, {"num": 12, "estado": "libre"}]
                },
                {
                    "letra": "C",
                    "es_vip": False,
                    "asientos_izq": [{"num": 1, "estado": "libre"}, {"num": 2, "estado": "libre"}, {"num": 3, "estado": "libre"}],
                    "asientos_centro": [
                        {"num": 4, "estado": "libre"}, {"num": 5, "estado": "libre"},
                        {"num": 6, "estado": "libre"}, {"num": 7, "estado": "libre"},
                        {"num": 8, "estado": "libre"}, {"num": 9, "estado": "libre"}
                    ],
                    "asientos_der": [{"num": 10, "estado": "libre"}, {"num": 11, "estado": "libre"}, {"num": 12, "estado": "libre"}]
                },
                {
                    "letra": "D",
                    "es_vip": False,
                    "asientos_izq": [{"num": 1, "estado": "libre"}, {"num": 2, "estado": "libre"}, {"num": 3, "estado": "libre"}],
                    "asientos_centro": [
                        {"num": 4, "estado": "libre"}, {"num": 5, "estado": "ocupada"},
                        {"num": 6, "estado": "ocupada"}, {"num": 7, "estado": "ocupada"},
                        {"num": 8, "estado": "ocupada"}, {"num": 9, "estado": "libre"}
                    ],
                    "asientos_der": [{"num": 10, "estado": "libre"}, {"num": 11, "estado": "libre"}, {"num": 12, "estado": "libre"}]
                },
                {
                    "letra": "E",
                    "es_vip": False,
                    "asientos_izq": [{"num": 1, "estado": "libre"}, {"num": 2, "estado": "libre"}, {"num": 3, "estado": "libre"}],
                    "asientos_centro": [
                        {"num": 4, "estado": "libre"}, {"num": 5, "estado": "libre"},
                        {"num": 6, "estado": "libre"}, {"num": 7, "estado": "seleccionada"},
                        {"num": 8, "estado": "seleccionada"}, {"num": 9, "estado": "libre"}
                    ],
                    "asientos_der": [{"num": 10, "estado": "libre"}, {"num": 11, "estado": "libre"}, {"num": 12, "estado": "libre"}]
                },
                {
                    "letra": "F",
                    "es_vip": True,
                    "asientos_izq": [{"num": 1, "estado": "libre"}, {"num": 2, "estado": "libre"}, {"num": 3, "estado": "libre"}],
                    "asientos_centro": [
                        {"num": 4, "estado": "libre"}, {"num": 5, "estado": "libre"},
                        {"num": 6, "estado": "ocupada"}, {"num": 7, "estado": "ocupada"},
                        {"num": 8, "estado": "libre"}, {"num": 9, "estado": "libre"}
                    ],
                    "asientos_der": [{"num": 10, "estado": "libre"}, {"num": 11, "estado": "libre"}, {"num": 12, "estado": "libre"}]
                },
                {
                    "letra": "G",
                    "es_vip": True,
                    "asientos_izq": [{"num": 1, "estado": "libre"}, {"num": 2, "estado": "libre"}, {"num": 3, "estado": "libre"}],
                    "asientos_centro": [
                        {"num": 4, "estado": "libre"}, {"num": 5, "estado": "libre"},
                        {"num": 6, "estado": "libre"}, {"num": 7, "estado": "libre"},
                        {"num": 8, "estado": "libre"}, {"num": 9, "estado": "libre"}
                    ],
                    "asientos_der": [{"num": 10, "estado": "libre"}, {"num": 11, "estado": "libre"}, {"num": 12, "estado": "libre"}]
                },
                {
                    "letra": "H",
                    "es_vip": False,
                    "asientos_izq": [{"num": 1, "estado": "libre"}, {"num": 2, "estado": "libre"}, {"num": 3, "estado": "libre"}],
                    "asientos_centro": [
                        {"num": 4, "estado": "libre"}, {"num": 5, "estado": "libre"},
                        {"num": 6, "estado": "libre"}, {"num": 7, "estado": "libre"},
                        {"num": 8, "estado": "libre"}, {"num": 9, "estado": "libre"}
                    ],
                    "asientos_der": [{"num": 10, "estado": "libre"}, {"num": 11, "estado": "libre"}, {"num": 12, "estado": "libre"}]
                },
            ]
        },
        "resumen": {
            "total_butacas": 2,
            "ubicaciones": [
                {
                    "id": "E-7",
                    "fila": "E",
                    "butaca": 7,
                    "categoria": "General 4D",
                    "precio": 8500,
                    "precio_formato": "$8.500"
                },
                {
                    "id": "E-8",
                    "fila": "E",
                    "butaca": 8,
                    "categoria": "General 4D",
                    "precio": 8500,
                    "precio_formato": "$8.500"
                }
            ],
            "subtotal": 17000,
            "subtotal_formato": "$17.000",
            "cargo_servicio": 0,
            "cargo_servicio_texto": "Bonificado $0",
            "total": 17000,
            "total_formato": "$17.000"
        }
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
