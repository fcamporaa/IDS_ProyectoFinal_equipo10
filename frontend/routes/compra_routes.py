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
