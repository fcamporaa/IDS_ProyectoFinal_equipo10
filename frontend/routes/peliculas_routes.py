from flask import Blueprint, abort, render_template

from services.peliculas_service import obtener_detalle_pelicula
from utils.peliculas import armar_detalle_pelicula

peliculas_bp = Blueprint("peliculas", __name__, url_prefix="/peliculas")


@peliculas_bp.route("/<int:id_pelicula>")
def detalle_pelicula(id_pelicula):
    """
    Renderiza la ficha y las funciones de una película leídas del backend.
    Solo si el backend no responde se usa el contexto genérico de más abajo.
    """
    pelicula, estado = obtener_detalle_pelicula(id_pelicula)
    if estado == 200 and isinstance(pelicula, dict):
        return render_template(
            "pelicula_detalle.html", p=armar_detalle_pelicula(pelicula)
        )
    if estado == 404:
        abort(404)

    datos_pelicula = {
        "id_pelicula": id_pelicula,
        "titulo": "Dune: Parte Dos",
        "titulo_original": "Dune: Part Two",
        "puntuacion_imdb": "8.8 / 10 (IMDb)",
        "porcentaje_critica": "95% Crítica Positiva",
        "poster_url": "https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg",
        "banner_url": "/static/images/dune_trailer_banner.jpg",
        "formato_destacado": "SALA 4D",
        "clasificacion": "+16",
        "duracion_min": 166,
        "duracion_legible": "166 min (2h 46m)",
        "idioma_formato": "Subtitulada",
        "anio": 2024,
        "sinopsis": (
            "Paul Atreides se une a Chani y a los Fremen mientras busca venganza "
            "contra los conspiradores que destruyeron a su familia, enfrentando la encrucijada "
            "entre el amor de su vida y el destino del universo entero. La travesía mística y bélica "
            "en las dunas de Arrakis alcanza su clímax definitivo con la profecía de Muad'Dib."
        ),
        "direccion": "Denis Villeneuve",
        "reparto": "Timothée Chalamet, Zendaya, Rebecca Ferguson, Javier Bardem",
        "generos": ["Ciencia Ficción", "Aventura"],
        "distribuidora": "Warner Bros. Pictures",
        "tecnologia_sala": "D-BOX Motion & Atmos",
        "trailer_url": "https://www.youtube.com/embed/Way9Dexny3w?autoplay=1",
        "trailer_duracion": "2:45 MIN",
        "complejos": [
            {
                "id": "centro",
                "etiqueta": "SEDE PRINCIPAL",
                "nombre": "Cine Paradiso Centro",
                "direccion": "Av. Corrientes 1240, CABA",
                "badges": ["4D Atmos", "3D", "2D Láser"],
                "seleccionado": True,
            },
            {
                "id": "palermo",
                "etiqueta": "COMPLEJO SOHO",
                "nombre": "Cine Paradiso Palermo",
                "direccion": "Humboldt 1920, Palermo Soho",
                "badges": ["2D", "2D Láser", "Sala VIP"],
                "seleccionado": False,
            },
            {
                "id": "belgrano",
                "etiqueta": "COMPLEJO NORTE",
                "nombre": "Cine Paradiso Belgrano",
                "direccion": "Av. Cabildo 2100, CABA",
                "badges": ["4D Atmos", "2D Láser"],
                "seleccionado": False,
            },
        ],
        "fechas": [
            {"id": "hoy", "etiqueta": "Hoy 24 Oct", "activa": True},
            {"id": "manana", "etiqueta": "Mañana 25 Oct", "activa": False},
            {"id": "sabado", "etiqueta": "Sábado 26 Oct", "activa": False},
            {"id": "domingo", "etiqueta": "Domingo 27 Oct", "activa": False},
        ],
        "salas_funciones": [
            {
                "sala_id": 1,
                "badge_tipo": "4D ATMOS",
                "badge_clase": "badge-4d",
                "nombre": "Sala 1 — Cinema Sensations 4D",
                "descripcion": "Efectos de viento, vibración, agua, aromas y sonido Dolby Atmos • Subtitulada",
                "precio": "$12.500",
                "precio_numero": 12500,
                "funciones": [
                    {
                        "id_funcion": 101,
                        "hora": "16:30 hs",
                        "idioma": "Subtitulada",
                        "disponibilidad": "42 libres",
                        "estado": "alta",
                        "seleccionada": False,
                    },
                    {
                        "id_funcion": 102,
                        "hora": "19:30 hs",
                        "idioma": "Subtitulada",
                        "disponibilidad": "14 libres",
                        "estado": "baja",
                        "seleccionada": True,
                    },
                    {
                        "id_funcion": 103,
                        "hora": "22:45 hs",
                        "idioma": "Subtitulada",
                        "disponibilidad": "56 libres",
                        "estado": "alta",
                        "seleccionada": False,
                    },
                ],
            },
            {
                "sala_id": 2,
                "badge_tipo": "3D DIGITAL",
                "badge_clase": "badge-3d",
                "nombre": "Sala 2 — RealD 3D Grand Hall",
                "descripcion": "Proyección Láser 4K de alto brillo con anteojos ergonómicos • Doblada al Castellano",
                "precio": "$9.800",
                "precio_numero": 9800,
                "funciones": [
                    {
                        "id_funcion": 201,
                        "hora": "17:15 hs",
                        "idioma": "Castellano",
                        "disponibilidad": "34 libres",
                        "estado": "alta",
                        "seleccionada": False,
                    },
                    {
                        "id_funcion": 202,
                        "hora": "20:15 hs",
                        "idioma": "Castellano",
                        "disponibilidad": "21 libres",
                        "estado": "baja",
                        "seleccionada": False,
                    },
                ],
            },
            {
                "sala_id": 3,
                "badge_tipo": "2D LÁSER",
                "badge_clase": "badge-2d",
                "nombre": "Sala 3 — Christie 4K Audio Surround 7.1",
                "descripcion": "Resolución ultra nítida, audio original sin compresión • Subtitulada",
                "precio": "$8.500",
                "precio_numero": 8500,
                "funciones": [
                    {
                        "id_funcion": 301,
                        "hora": "18:00 hs",
                        "idioma": "Subtitulada",
                        "disponibilidad": "70 libres",
                        "estado": "alta",
                        "seleccionada": False,
                    },
                    {
                        "id_funcion": 302,
                        "hora": "21:00 hs",
                        "idioma": "Subtitulada",
                        "disponibilidad": "73 libres",
                        "estado": "alta",
                        "seleccionada": False,
                    },
                    {
                        "id_funcion": 303,
                        "hora": "23:30 hs",
                        "idioma": "Trasnocha • 140 libres",
                        "disponibilidad": "140 libres",
                        "estado": "alta",
                        "seleccionada": False,
                    },
                ],
            },
        ],
        "seleccion_inicial": {
            "complejo": "Cine Paradiso Centro",
            "fecha": "Hoy 24 Oct",
            "sala": "Sala 1 (4D Atmos)",
            "hora": "19:30 hs",
            "precio": "$12.500",
            "id_funcion": 102,
        },
    }

    return render_template("pelicula_detalle.html", p=datos_pelicula)
