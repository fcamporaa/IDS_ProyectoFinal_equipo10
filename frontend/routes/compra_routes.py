from flask import Blueprint, render_template

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


@compra_bp.route("/servicios")
def seleccion_servicios():
    """
    Renderiza la pantalla de selección de servicios complementarios y combos (Candy Bar).
    Muestra el catálogo con combos, pochoclos, bebidas y extras, junto al resumen de compra acumulado.
    """
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
                    "subtotal": 17000,
                    "subtotal_formato": "$17.000",
                }
            ],
            "subtotal": 17000,
            "subtotal_formato": "$17.000",
        },
        "categorias_filtro": [
            {"id": "todos", "nombre": "Todos los Combos"},
            {"id": "pochoclos", "nombre": "Pochoclos"},
            {"id": "bebidas", "nombre": "Bebidas"},
            {"id": "snacks", "nombre": "Snacks & Dulces"},
            {"id": "estacionamiento", "nombre": "Estacionamiento & VIP"},
        ],
        "servicios": [
            {
                "id_servicio": 1,
                "nombre": "Combo Mega Paradiso",
                "categoria": "combos pochoclos bebidas",
                "descripcion": "Balde gigante de pochoclos salados o dulces + 2 gaseosas grandes 1L + golosina a elección en candy bar.",
                "precio": 14500,
                "precio_formato": "$14.500",
                "badge_top": "MÁS VENDIDO",
                "badge_top_tipo": "badge-gold",
                "badge_image_bottom": "Tamaño Gigante",
                "cantidad": 1,
                "imagen_url": "https://images.unsplash.com/photo-1572177812156-58036aae439c?w=600&auto=format&fit=crop&q=80",
            },
            {
                "id_servicio": 2,
                "nombre": "Combo Clásico Dúo",
                "categoria": "combos pochoclos bebidas",
                "descripcion": "1 Balde mediano de pochoclos recién hechos + 2 gaseosas medianas 500ml.",
                "precio": 10200,
                "precio_formato": "$10.200",
                "badge_top": None,
                "badge_top_tipo": None,
                "badge_image_bottom": None,
                "cantidad": 0,
                "imagen_url": "https://images.unsplash.com/photo-1585647347384-2593bc35786b?w=600&auto=format&fit=crop&q=80",
            },
            {
                "id_servicio": 3,
                "nombre": "Combo Individual",
                "categoria": "combos pochoclos bebidas",
                "descripcion": "1 Bolsa de pochoclos crocantes + 1 gaseosa 500ml línea Coca-Cola.",
                "precio": 6800,
                "precio_formato": "$6.800",
                "badge_top": None,
                "badge_top_tipo": None,
                "badge_image_bottom": None,
                "cantidad": 0,
                "imagen_url": "https://images.unsplash.com/photo-1505686994434-e3cc5abf1330?w=600&auto=format&fit=crop&q=80",
            },
            {
                "id_servicio": 4,
                "nombre": "Voucher Estacionamiento Prepago (3 hs cubiertas)",
                "categoria": "estacionamiento",
                "descripcion": "Acceso exclusivo cubierto por 3 horas en cochera de Av. Corrientes 1240. Validación automática con QR.",
                "precio": 4500,
                "precio_formato": "$4.500",
                "badge_top": "PARADISO CENTRO",
                "badge_top_tipo": "badge-cyan",
                "badge_image_bottom": "3 Horas Cubiertas",
                "cantidad": 1,
                "imagen_url": "https://images.unsplash.com/photo-1506521781263-d8422e82f27a?w=600&auto=format&fit=crop&q=80",
            },
            {
                "id_servicio": 5,
                "nombre": "Nachos con Queso Cheddar Caliente",
                "categoria": "snacks",
                "descripcion": "Porción generosa de nachos crujientes con queso cheddar fundido caliente en bandeja térmica.",
                "precio": 5200,
                "precio_formato": "$5.200",
                "badge_top": None,
                "badge_top_tipo": None,
                "badge_image_bottom": None,
                "cantidad": 0,
                "imagen_url": "https://images.unsplash.com/photo-1513456852971-30c0b8199d4d?w=600&auto=format&fit=crop&q=80",
            },
            {
                "id_servicio": 6,
                "nombre": "Gaseosa Extra Grande (Línea Coca-Cola)",
                "categoria": "bebidas",
                "descripcion": "1000ml a elección: Coca-Cola original, Sin Azúcar, Sprite o Fanta con hielo frappe.",
                "precio": 3500,
                "precio_formato": "$3.500",
                "badge_top": None,
                "badge_top_tipo": None,
                "badge_image_bottom": None,
                "cantidad": 0,
                "imagen_url": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=600&auto=format&fit=crop&q=80",
            },
        ],
        "candy_seleccionado": {
            "items": [
                {
                    "id_servicio": 1,
                    "nombre": "Combo Mega Paradiso",
                    "descripcion": "Balde gigante + 2 gaseosas 1L",
                    "cantidad": 1,
                    "subtotal": 14500,
                    "subtotal_formato": "$14.500",
                },
                {
                    "id_servicio": 4,
                    "nombre": "Voucher Estacionamiento Prepago (3 hs cubi...",
                    "descripcion": "3 hs. cubiertas - Centro",
                    "cantidad": 1,
                    "subtotal": 4500,
                    "subtotal_formato": "$4.500",
                },
            ],
            "total_items": 2,
            "subtotal": 19000,
            "subtotal_formato": "$19.000",
        },
        "resumen": {
            "subtotal_entradas": 17000,
            "subtotal_entradas_formato": "$17.000",
            "subtotal_candy": 19000,
            "subtotal_candy_formato": "$19.000",
            "cargos_servicio_texto": "100% Bonificado",
            "total": 36000,
            "total_formato": "$36.000",
        },
    }

    return render_template("seleccion_servicios.html", c=datos_compra)


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
